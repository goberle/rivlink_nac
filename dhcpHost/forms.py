# -*- coding: Utf-8 -*-
from django import forms
from models import dhcpHost
from functions import *

class AddGatewayForm(forms.Form):
	name = forms.CharField(label="Nom", max_length=20)
	mac_address = forms.RegexField(label="Adresse MAC", max_length=17, regex=r'^[0-9a-f]{2}([:][0-9a-f]{2}){5}$', error_messages = {'invalid': "L'adresse MAC n'est pas valide. Elle doit être sous la forme XX:XX:XX:XX:XX:XX."})
	
	def __init__(self, user, ip, *args, **kwargs):
        	self.user = user
		self.ip = ip
        	super(AddGatewayForm, self).__init__(*args, **kwargs)

	def clean_name(self):
		name = self.cleaned_data['name']
		names_found = dhcpHost.objects.filter(name=name,owner=self.user.id)
		if len(names_found) >= 1:
			raise forms.ValidationError("Ce nom est déjà utilisé.")
		return name

	def clean_mac_address(self):
		mac_address = self.cleaned_data['mac_address']
	        macs_found = dhcpHost.objects.filter(mac_address__iexact=mac_address)
		if len(macs_found) >= 1:
			raise forms.ValidationError("Cette addresse MAC est déjà utilisé.")
		return mac_address
	
	def save(self):
		self.dhcpHost = dhcpHost()
        	self.dhcpHost.owner_id = self.user.id
		self.dhcpHost.name = self.cleaned_data['name']
		self.dhcpHost.mac_address = self.cleaned_data['mac_address']
		self.dhcpHost.ip_address = self.ip
		self.dhcpHost.state = 1
		self.dhcpHost.is_gateway = 1
            	self.dhcpHost.save()
        	return self.dhcpHost

class ModifyGatewayForm(forms.Form):
	name = forms.CharField(label="Nom", max_length=20)
	mac_address = forms.RegexField(label="Adresse MAC", max_length=17, regex=r'^[0-9a-f]{2}([:][0-9a-f]{2}){5}$', error_messages = {'invalid': "L'adresse MAC n'est pas valide. Elle doit être sous la forme XX:XX:XX:XX:XX:XX."})

	def __init__(self, gateway, user, *args, **kwargs):
		self.user = user
		self.dhcpHost = gateway
		super(ModifyGatewayForm, self).__init__(*args, **kwargs)
	
	def clean_name(self):
		name = self.cleaned_data['name']
		if name != self.dhcpHost.name:
			names_found = dhcpHost.objects.filter(name=name,owner=self.user.id)
			if len(names_found) >= 1:
				raise forms.ValidationError("Ce nom est déjà utilisé.")
		return name

	def clean_mac_address(self):
		mac_address = self.cleaned_data['mac_address']
		if mac_address != self.dhcpHost.mac_address:
	        	macs_found = dhcpHost.objects.filter(mac_address__iexact=mac_address)
			if len(macs_found) >= 1:
				raise forms.ValidationError("Cette addresse MAC est déjà utilisé.")
		return mac_address
	
	def save(self):
		self.dhcpHost.name = self.cleaned_data['name']
		self.dhcpHost.mac_address = self.cleaned_data['mac_address']
            	self.dhcpHost.save()
        	return self.dhcpHost

class AddConfigGatewayForm(forms.Form):
	name = forms.CharField(label="Nom", max_length=20)
	mac_address = forms.RegexField(label="Adresse MAC", max_length=17, regex=r'^[0-9a-f]{2}([:][0-9a-f]{2}){5}$', error_messages = {'invalid': "L'adresse MAC n'est pas valide. Elle doit être sous la forme XX:XX:XX:XX:XX:XX."})
	ip_address = forms.BooleanField(label="Adresse IP fixe", required=False)
	
	def __init__(self, user, *args, **kwargs):
        	self.user = user
        	super(AddConfigGatewayForm, self).__init__(*args, **kwargs)
		# On déclare le field ici pour qu'il soit mis à jour à chaque appel du formulaire
		choices = [(c[0], '%s@%s'%(c[1],c[2])) \
			for c in dhcpHost.objects.filter(is_gateway=1, state=1).values_list('ip_address','name','owner__username')]
		self.fields['gateway'] = forms.ChoiceField(choices=choices) 

	def clean_name(self):
		name = self.cleaned_data['name']
		names_found = dhcpHost.objects.filter(name=name,owner=self.user.id)
		if len(names_found) >= 1:
			raise forms.ValidationError("Ce nom est déjà utilisé.")
		return name

	def clean_mac_address(self):
		mac_address = self.cleaned_data['mac_address']
	        macs_found = dhcpHost.objects.filter(mac_address__iexact=mac_address)
		if len(macs_found) >= 1:
			raise forms.ValidationError("Cette addresse MAC est déjà utilisé.")
		return mac_address

	def clean_ip_address(self):
		if self.cleaned_data['ip_address'] == True:
			ip = get_ip()
			if ip:
				return ip
			else:
				raise forms.ValidationError("Il n'y a plus d'adresses IP fixe disponible.")
		return None

	def save(self):
		self.dhcpHost = dhcpHost()
        	self.dhcpHost.owner_id = self.user.id
		self.dhcpHost.name = self.cleaned_data['name']
		self.dhcpHost.mac_address = self.cleaned_data['mac_address']
		self.dhcpHost.ip_address = self.cleaned_data['ip_address']
		self.dhcpHost.gateway = self.cleaned_data['gateway']
		self.dhcpHost.state = 0
		self.dhcpHost.is_gateway = 0
            	self.dhcpHost.save()
        	return self.dhcpHost

class AddConfigIPForm(forms.Form):
	name = forms.CharField(label="Nom", max_length=20)
	mac_address = forms.RegexField(label="Adresse MAC", max_length=17, regex=r'^[0-9a-f]{2}([:][0-9a-f]{2}){5}$', error_messages = {'invalid': "L'adresse MAC n'est pas valide. Elle doit être sous la forme XX:XX:XX:XX:XX:XX."})
	
	def __init__(self, user, ip, *args, **kwargs):
        	self.user = user
		self.ip = ip
        	super(AddConfigIPForm, self).__init__(*args, **kwargs)

	def clean_name(self):
		name = self.cleaned_data['name']
		names_found = dhcpHost.objects.filter(name=name,owner=self.user.id)
		if len(names_found) >= 1:
			raise forms.ValidationError("Ce nom est déjà utilisé.")
		return name

	def clean_mac_address(self):
		mac_address = self.cleaned_data['mac_address']
	        macs_found = dhcpHost.objects.filter(mac_address__iexact=mac_address)
		if len(macs_found) >= 1:
			raise forms.ValidationError("Cette addresse MAC est déjà utilisé.")
		return mac_address

	def save(self):
		self.dhcpHost = dhcpHost()
        	self.dhcpHost.owner_id = self.user.id
		self.dhcpHost.name = self.cleaned_data['name']
		self.dhcpHost.mac_address = self.cleaned_data['mac_address']
		self.dhcpHost.ip_address = self.ip
		self.dhcpHost.gateway = None
		self.dhcpHost.state = 1
		self.dhcpHost.is_gateway = 0
            	self.dhcpHost.save()
        	return self.dhcpHost
