# -*- coding: Utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class DhcpGateway(models.Model):
    owner = models.ForeignKey(User)
    ip_address = models.IPAddressField(unique=True, primary_key=True)

class DhcpHost(models.Model):
    VALIDATED = 'V'
    WAITING_VALIDATION = 'W'
    UNLINKED = 'U'
    STATES = (
        (VALIDATED, 'Validated'),
        (WAITING_VALIDATION, 'Waiting validation'),
        (UNLINKED, 'Unlinked')
    )
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    mac_address = models.CharField(max_length=17, unique=True)
    gateway = models.ForeignKey(DhcpGateway)
    state = models.CharField(max_length=1, choices=STATES)
