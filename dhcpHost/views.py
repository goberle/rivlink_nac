# -*- coding: Utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from dhcpHost.forms import AddGatewayForm, ModifyGatewayForm, AddConfigGatewayForm, AddConfigIPForm
from dhcpHost.models import dhcpHost
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from functions import *
from dhcpHostLDAP import dhcpHostLDAP

def home(request):
	if request.user.is_authenticated():
		return render(request, 'dhcpHost/home.html')
	else:
		return render(request, 'portal.html')

@login_required
def gateways(request,
             template_name='dhcpHost/gateways.html'):
    	my_gateways = dhcpHost.objects.filter(owner_id=request.user.id, is_gateway=1)
	my_gateways_list = my_gateways.values_list('ip_address', flat=True)

	my_clients = dhcpHost.objects.filter(gateway__in=my_gateways_list, is_gateway=0, state=1)	
	for client in my_clients:
		client.gateway = '%s'%(dhcpHost.objects.filter(ip_address=client.gateway, is_gateway=1).values_list('name')[0][0])

	my_demands = dhcpHost.objects.filter(gateway__in=my_gateways_list, is_gateway=0, state=0)
	for demand in my_demands:
		demand.gateway = '%s'%(dhcpHost.objects.filter(ip_address=demand.gateway, is_gateway=1).values_list('name')[0][0])

	return TemplateResponse(request, template_name, {'my_gateways': my_gateways, 'my_clients': my_clients, 'my_demands': my_demands})

@login_required
def add_gateway(request,
                template_name='dhcpHost/add_gateway.html',
                post_change_redirect='/dhcpHost/gateways/',
                add_gateway_form=AddGatewayForm):
	if request.method == "POST":
		ip = get_ip()
		if not ip:
			error = "Il n'y a plus d'adresses IP fixes disponibles pour créer une nouvelle passerelle."
			return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
		form = add_gateway_form(user=request.user, ip=ip, data=request.POST)
       		if form.is_valid():
			dhcpHost = form.save()
			try:
				ldap = dhcpHostLDAP()
				ldap.add(dhcpHost.id,dhcpHost.mac_address,dhcpHost.ip_address)
				ldap.close()
			except:
				dhcpHost.delete()
				error = "Connexion au serveur LDAP impossible."
				return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            		return HttpResponseRedirect(post_change_redirect)
    	else:
	    	form = add_gateway_form(user=request.user, ip=None)
    	return TemplateResponse(request, template_name, {'form': form,})

@login_required
def delete_gateway(request,
		   dhcpHost_id,
		   post_delete_redirect='/dhcpHost/gateways/'):
	try:
		gateway = dhcpHost.objects.get(owner=request.user.id, id=dhcpHost_id, is_gateway=1)
		clients = dhcpHost.objects.filter(gateway=gateway.ip_address, is_gateway=0)
		try:
			ldap = dhcpHostLDAP()
			for client in clients:
				if client.state == 1:
					ldap.delete(client.id)
				client.state = 3 
				client.save()
			ldap.delete(gateway.id)
			ldap.close()
			gateway.delete()
			return HttpResponseRedirect(post_delete_redirect)
		except:
			error = "Connexion au serveur LDAP impossible."
			return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
	except:
		return HttpResponseRedirect(post_delete_redirect)

@login_required
def modify_gateway(request,
		   dhcpHost_id,
		   post_modify_redirect='/dhcpHost/gateways/',
		   template_name='dhcpHost/modify_gateway.html',
		   modify_gateway_form=ModifyGatewayForm):
	try:
		gateway = dhcpHost.objects.get(id=dhcpHost_id, owner=request.user.id, is_gateway=1)
		if request.method == "POST":
			form = modify_gateway_form(gateway=gateway, user=request.user, data=request.POST)
			if form.is_valid():
				#MODIFY LDAP
				form.save()
				return HttpResponseRedirect(post_modify_redirect)
		else:
			form = modify_gateway_form(gateway, user=request.user, initial={'name': gateway.name, 'mac_address': gateway.mac_address})
		return TemplateResponse(request, template_name, {'form': form})
	except:
		return HttpResponseRedirect(post_modify_redirect)

@login_required
def accept_client(request,
		  dhcpHost_id,
		  post_accept_redirect='/dhcpHost/gateways/'):
	try:
		client = dhcpHost.objects.get(id=dhcpHost_id, is_gateway=0, state=0)
		my_gateways = dhcpHost.objects.filter(owner_id=request.user.id, is_gateway=1).values_list('ip_address', flat=True)
		if client.gateway in my_gateways:
			try:
				ldap = dhcpHostLDAP()
				ldap.add(client.id,client.mac_address,ip_address=client.ip_address,gateway=client.gateway)
				ldap.close()
			except:
				error = "Connexion au serveur LDAP impossible."
				return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
			client.state = 1
			client.save()
		return HttpResponseRedirect(post_accept_redirect)
	except:
		return HttpResponseRedirect(post_accept_redirect)

@login_required
def refuse_client(request,
		  dhcpHost_id,
		  post_refuse_redirect='/dhcpHost/gateways/'):
	try:
		client = dhcpHost.objects.get(id=dhcpHost_id, is_gateway=0, state=0)
		my_gateways = dhcpHost.objects.filter(owner_id=request.user.id, is_gateway=1).values_list('ip_address', flat=True)
		if client.gateway in my_gateways:
			client.state = 2
			client.save()
		return HttpResponseRedirect(post_refuse_redirect)
	except:
		return HttpResponseRedirect(post_refuse_redirect)

@login_required
def delete_client(request,
		  dhcpHost_id,
		  post_delete_redirect='/dhcpHost/gateways/'):
	try:
		client = dhcpHost.objects.get(id=dhcpHost_id, is_gateway=0, state=1)
		my_gateways = dhcpHost.objects.filter(owner_id=request.user.id, is_gateway=1).values_list('ip_address', flat=True)
		if client.gateway in my_gateways:
			try:
				ldap = dhcpHostLDAP()
				ldap.delete(client.id)
				ldap.close()
			except:
				error = "Connexion au serveur LDAP impossible."
				return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
			client.state = 3
			client.save()
		return HttpResponseRedirect(post_delete_redirect)
	except:
		return HttpResponseRedirect(post_delete_redirect)

@login_required
def configs(request,
	    template_name='dhcpHost/configs.html'):
	my_configs = dhcpHost.objects.filter(owner=request.user.id, is_gateway=0)
	for config in my_configs:
		config.gateway = dhcpHost.objects.filter(ip_address=config.gateway, is_gateway=1).values_list('name', 'owner__username')
		if config.gateway and config.state < 3:
			config.gateway = '%s@%s'%(config.gateway[0][0],config.gateway[0][1])
		else:
			config.gateway = ''
	return TemplateResponse(request, template_name, {'my_configs': my_configs})

@login_required
def add_config_gateway(request,
               template_name='dhcpHost/add_config_gateway.html',
               post_change_redirect='/dhcpHost/configs/',
               add_config_gateway_form=AddConfigGatewayForm):
	if request.method == "POST":
		form = add_config_gateway_form(user=request.user, data=request.POST)
       		if form.is_valid():
            		form.save()
            		return HttpResponseRedirect(post_change_redirect)
    	else:
		form = add_config_gateway_form(user=request.user, initial={'mac_address': get_mac(request.META['REMOTE_ADDR'])})

    	return TemplateResponse(request, template_name, {'form': form,})

@login_required
def add_config_ip(request,
               template_name='dhcpHost/add_config_ip.html',
               post_change_redirect='/dhcpHost/configs/',
               add_config_ip_form=AddConfigIPForm):
	if request.method == "POST":
		ip = get_ip()
		if not ip:
			error = "Il n'y a plus d'adresses IP fixe disponible."
			return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
		form = add_config_ip_form(user=request.user, ip=ip, data=request.POST)
       		if form.is_valid():
			dhcpHost = form.save()
			try:
				ldap = dhcpHostLDAP()
				ldap.add(dhcpHost.id,dhcpHost.mac_address,dhcpHost.ip_address)
				ldap.close()
			except:
				dhcpHost.delete()
				error = "Connexion au serveur LDAP impossible."
				return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
            		return HttpResponseRedirect(post_change_redirect)
    	else:
		form = add_config_ip_form(user=request.user, ip=None, initial={'mac_address': get_mac(request.META['REMOTE_ADDR'])})

    	return TemplateResponse(request, template_name, {'form': form,})

@login_required
def delete_config(request,
		  dhcpHost_id,
		  post_delete_redirect='/dhcpHost/configs/'):
	try:
		config = dhcpHost.objects.get(owner=request.user.id, id=dhcpHost_id, is_gateway=0)
		if config.state == 1:
			try:
				ldap = dhcpHostLDAP()
				ldap.delete(config.id)
				ldap.close()
			except:
				error = "Connexion au serveur LDAP impossible."
				return TemplateResponse(request, 'dhcpHost/error.html', {'error': error})
		config.delete()
		return HttpResponseRedirect(post_delete_redirect)
	except:
		return HttpResponseRedirect(post_delete_redirect)

