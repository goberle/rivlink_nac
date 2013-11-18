# -*- coding: Utf-8 -*-
from django import forms
from models import DhcpHost, DhcpGateway
from functions import *

class AddGatewayForm(forms.Form):
    
    name = forms.RegexField(
        label="Identifiant de la passerelle",
        help_text="Par exemple, le nom de la machine (entre 3 et 12 caractères, lettres seulement)",
        max_length=12, min_length=3,
        regex=r'^[a-zA-Z]+$',
        error_messages={'invalid': "L'identifiant ne doit comporter que des lettres"}
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AddGatewayForm, self).__init__(*args, **kwargs)
        choices = [(c, c) for c in get_ip_list()]
        self.fields['ip_address'] = forms.ChoiceField(label="Passerelle", choices=choices) 
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if DhcpGateway.objects.filter(name=name, owner=self.user.id):
            raise forms.ValidationError("Cet identifiant est déjà utilisé.")
        return name

    def clean_ip_address(self):
        ip_address = self.cleaned_data['ip_address']
        if not is_ip_authorized(ip_address):
            raise forms.ValidationError("Cette addresse IP n'est pas autorisée, choisissez en une dans la liste.")
        return ip_address
    
    def get_dhcp_gateway(self):
        gw = DhcpGateway()
        gw.owner_id = self.user.id
        gw.name = self.cleaned_data['name']
        gw.ip_address = self.cleaned_data['ip_address']
        return gw

class AddHostForm(forms.Form):
    name = forms.CharField(label="Identifiant", max_length=20)
    mac_address = forms.RegexField(
            label="Adresse MAC",
            max_length=17, regex=r'^[0-9a-f]{2}([:][0-9a-f]{2}){5}$',
            error_messages = {'invalid': "L'adresse MAC n'est pas valide. Elle doit être sous la forme XX:XX:XX:XX:XX:XX."},
            widget=forms.TextInput(attrs={'placeholder': 'XX:XX:XX:XX:XX:XX'})
    )
    ip_address = forms.BooleanField(label="Besoin d'une IP fixe (serveur)", required=False)
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AddHostForm, self).__init__(*args, **kwargs)
        # On déclare le field ici pour qu'il soit mis à jour à chaque appel du formulaire
        choices = [(c[0], '%s (%s)'%(c[1], c[0])) \
            for c in DhcpGateway.objects.all().values_list('ip_address','owner__username')]
        self.fields['gateway'] = forms.ChoiceField(label="Passerelle", choices=choices) 

    def clean_name(self):
        name = self.cleaned_data['name']
        if DhcpHost.objects.filter(name=name, owner=self.user.id):
            raise forms.ValidationError("Cet identifiant est déjà utilisé.")
        return name

    def clean_mac_address(self):
        mac_address = self.cleaned_data['mac_address']
        if DhcpHost.objects.filter(mac_address__iexact=mac_address):
            raise forms.ValidationError("Cette addresse MAC est déjà utilisée.")
        return mac_address

    def clean_ip_address(self):
        if self.cleaned_data['ip_address'] == True:
            ip = get_ip()
            if ip:
                return ip
            else:
                raise forms.ValidationError("Il n'y a plus d'adresses IP fixes disponibles.")
        return None

    def get_dhcp_host(self):
        host = DhcpHost()
        host.owner_id = self.user.id
        host.name = self.cleaned_data['name']
        host.mac_address = self.cleaned_data['mac_address']
        host.gateway = DhcpGateway.objects.get(ip_address=self.cleaned_data['gateway'])
        host.state = DhcpHost.WAITING_VALIDATION
        return host

