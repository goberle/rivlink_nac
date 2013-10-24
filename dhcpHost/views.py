# -*- coding: Utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from dhcpHost.forms import AddGatewayForm, AddHostForm
from dhcpHost.models import DhcpHost, DhcpGateway
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from functions import *
from omapi import NacOmapi

def home(request):
    if request.user.is_authenticated():
        return render(request, 'dhcpHost/home.html')
    else:
        return render(request, 'portal.html')

@login_required
def gateways(request, template_name='dhcpHost/gateways.html'):
    my_gateways = DhcpGateway.objects.filter(owner_id=request.user.id)
    my_clients = DhcpHost.objects.filter(gateway__in=my_gateways, state=DhcpHost.VALIDATED) 
    my_demands = DhcpHost.objects.filter(gateway__in=my_gateways, state=DhcpHost.WAITING_VALIDATION)
    return TemplateResponse(request, template_name, {'my_gateways': my_gateways, 'my_clients': my_clients, 'my_demands': my_demands})

@login_required
def add_gateway(request, template_name='dhcpHost/add_gateway.html', post_change_redirect='/dhcpHost/gateways/', add_gateway_form=AddGatewayForm):
    form = add_gateway_form(user=request.user)
    if request.method == "POST":
        form = add_gateway_form(user=request.user, data=request.POST)
        if form.is_valid():
            gw = form.get_dhcp_gateway()
            if not gw.ip_address:
                error = "Il n'y a plus d'adresses IP fixes disponibles pour créer une nouvelle passerelle."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            gw.save()
            return HttpResponseRedirect(post_change_redirect)
        else:
            form = add_gateway_form(user=request.user)
    return TemplateResponse(request, template_name, {'form': form,})

@login_required
def delete_gateway(request, gw_id, post_delete_redirect='/dhcpHost/gateways/'):
    try:
        gateway = DhcpGateway.objects.get(owner=request.user.id, ip_address=gw_id)
        clients = DhcpHost.objects.filter(gateway__ip_address=gw_id)
        try:
            if len(clients) > 0:
                omapi = NacOmapi.get_instance()
                for client in clients:
                    if client.state == DhcpHost.VALIDATED:
                        omapi.del_host(client.mac_address)
                    client.state = DhcpHost.UNLINKED
                    client.save()
                omapi.close()
            gateway.delete()
            return HttpResponseRedirect(post_delete_redirect)
        except Exception as e:
            # TODO log !
            print e
            error = "Connexion au serveur DHCP impossible."
            return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
    except Exception as e:
        print e
        return HttpResponseRedirect(post_delete_redirect)

@login_required
def accept_client(request, dhcpHost_id, post_accept_redirect='/dhcpHost/gateways/'):
    try:
        client = DhcpHost.objects.get(id=dhcpHost_id, state=DhcpHost.WAITING_VALIDATION)
        my_gateways = DhcpGateway.objects.filter(owner_id=request.user.id).values_list('ip_address', flat=True)
        if client.gateway in my_gateways:
            try:
                omapi = NacOmapi.get_instance()
                omapi.add_host_with_gateway(client.mac_address, client.gateway.ip_address)
                omapi.close()
            except:
                error = "Connexion au serveur DHCP impossible."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            client.state = DhcpHost.VALIDATED
            client.save()
        return HttpResponseRedirect(post_accept_redirect)
    except:
        return HttpResponseRedirect(post_accept_redirect)

@login_required
def refuse_client(request, dhcpHost_id, post_refuse_redirect='/dhcpHost/gateways/'):
    try:
        client = DhcpHost.objects.get(id=dhcpHost_id, state=DhcpHost.WAITING_VALIDATION)
        my_gateways = DhcpGateway.objects.filter(owner_id=request.user.id).values_list('ip_address', flat=True)
        if client.gateway in my_gateways:
            client.state = DhcpHost.UNLINKED
            client.save()
        return HttpResponseRedirect(post_refuse_redirect)
    except:
        return HttpResponseRedirect(post_refuse_redirect)

@login_required
def delete_client(request, dhcpHost_id, post_delete_redirect='/dhcpHost/gateways/'):
    try:
        client = DhcpHost.objects.get(id=dhcpHost_id, state=DhcpHost.VALIDATED)
        my_gateways = DhcpGateway.objects.filter(owner_id=request.user.id).values_list('ip_address', flat=True)
        if client.gateway in my_gateways:
            try:
                omapi = NacOmapi.get_instance()
                omapi.del_host(client.mac_address)
                omapi.close()
                client.state = DhcpHost.UNLINKED
                client.save()
            except:
                error = "Connexion au serveur DHCP impossible."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
        return HttpResponseRedirect(post_delete_redirect)
    except:
        return HttpResponseRedirect(post_delete_redirect)

@login_required
def hosts(request, template_name='dhcpHost/hosts.html'):
    hosts = DhcpHost.objects.filter(owner=request.user.id)
    return TemplateResponse(request, template_name, {'hosts': hosts})

@login_required
def add_host(request, template_name='dhcpHost/add_host.html', post_change_redirect='/dhcpHost/hosts/', add_host_form=AddHostForm):
    form = add_host_form
    if request.method == "POST":
        form = add_host_form(user=request.user, data=request.POST)
        if form.is_valid():
            """
            ip = get_ip()
            if not ip:
                error = "Il n'y a plus d'adresses IP fixe disponible."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            """
            host = form.get_dhcp_host()
            try:
                omapi = NacOmapi.get_instance()
                # TODO Add IP
                omapi.add_host_with_gateway(host.mac_address, host.gateway.ip_address)
                omapi.close()
                host.save()
            except:
                host.delete()
                error = "Connexion au serveur DHCP impossible."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            return HttpResponseRedirect(post_change_redirect)
        else:
            form = add_host_form(user=request.user, initial={'mac_address': get_mac(request.META['REMOTE_ADDR'])})
    return TemplateResponse(request, template_name, {'form': form,})

@login_required
def delete_host(request, dhcpHost_id, post_delete_redirect='/dhcpHost/hosts/'):
    try:
        host = DhcpHost.objects.get(owner=request.user.id, id=dhcpHost_id)
        if host.state == DhcpHost.VALIDATED:
            try:
                omapi = NacOmapi.get_instance()
                omapi.del_host(host.mac_address)
                omapi.close()
                host.delete()
            except:
                error = "Connexion au serveur DHCP impossible."
                return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
        return HttpResponseRedirect(post_delete_redirect)
    except:
        return HttpResponseRedirect(post_delete_redirect)

