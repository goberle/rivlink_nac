from models import dhcpHost
import commands

def get_ip(range=["10.20.0.100","10.20.0.255"]):
	ips_used = dhcpHost.objects.all().values_list('ip_address', flat=True)
	ips_used_list = list()
	min = DottedIPToInt(range[0])
	max = DottedIPToInt(range[1])
	clean_ip = min
	for ip in ips_used:
		if ip:
			ips_used_list.append(DottedIPToInt(ip))

	while clean_ip < max:
		if clean_ip not in ips_used_list: 
			return IntToDottedIP(clean_ip)
		else:
			clean_ip += 1
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
	mac = commands.getoutput('sudo arp -n %s'%ip).split()
	try:
		mac = mac[8]
		return mac
	except IndexError:
		return None
