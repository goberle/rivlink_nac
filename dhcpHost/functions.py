from django.conf import settings
from models import dhcpHost
import commands
import re

def get_ip(range=settings.DHCP_FIXED_IP_RANGE):
	ips_used = dhcpHost.objects.all().exclude(ip_address__isnull=True).values_list('ip_address', flat=True)
	min_ip = DottedIPToInt(range[0])
	max_ip = DottedIPToInt(range[1])
	ips_used_list = list()
	for ip in ips_used:
		ips_used_list.append(DottedIPToInt(ip))

	while min_ip <= max_ip:
		if min_ip not in ips_used_list: 
			return IntToDottedIP(min_ip)
		else:
			min_ip += 1 
	return False

def IntToDottedIP(intip):
        octet = ''
        for exp in [3,2,1,0]:
                octet = octet + str(intip / ( 256 ** exp )) + "."
                intip = intip % ( 256 ** exp )
        return(octet.rstrip('.'))

def DottedIPToInt(dotted_ip):
        exp = 3
        intip = 0
        for quad in dotted_ip.split('.'):
                intip = intip + (int(quad) * (256 ** exp))
                exp = exp - 1
        return(intip)

def get_mac(ip):
	match = re.match("(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})", ip)
	if not match:
		return None
	mac = commands.getoutput('sudo arp -n %s'%ip).split()
	try:
		mac = mac[8]
		return mac
	except IndexError:
		return None
