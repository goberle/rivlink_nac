# -*- coding: Utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class dhcpHost(models.Model):
	owner = models.ForeignKey(User)
	name = models.CharField(max_length=20)
	mac_address = models.CharField(max_length=17,unique=True)
	ip_address = models.IPAddressField(null=True,unique=True)
	gateway = models.IPAddressField(null=True)
	is_gateway = models.BooleanField()
	state = models.IntegerField()
