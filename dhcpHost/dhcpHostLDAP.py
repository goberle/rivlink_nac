import ldap
import ldap.modlist as modlist
from django.conf import settings

class dhcpHostLDAP:

	def __init__(self):
		self.con = ldap.initialize(settings.LDAP_HOST)
		self.con.simple_bind_s(settings.LDAP_USER, settings.LDAP_PASSWORD)
		self.base_dn = settings.LDAP_BASE_DN

	def add(self, id, mac_address, ip_address=False, gateway=False):
		dn="cn=%s, %s"%(str(id), self.base_dn)

		attrs = {}
		attrs['objectclass'] = ['top','dhcpHost']
		attrs['cn'] = str(id)
		attrs['dhcpHWAddress'] = 'ethernet ' + str(mac_address)
		if ip_address:
			attrs['dhcpStatements'] = 'fixed-address ' + str(ip_address)
		if gateway:
			attrs['dhcpOption'] = 'routers ' + str(gateway)
		ldif = modlist.addModlist(attrs)
		self.con.add_s(dn,ldif)

	def delete(self,id):
		dn="cn=%s, %s"%(str(id), self.base_dn)
		self.con.delete_s(dn)

	def modify(self,id, old_mac, new_mac):
		return False

	def close(self):
		self.con.unbind_s()
