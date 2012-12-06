from django.conf.urls import patterns, url

urlpatterns = patterns('dhcpHost.views',
	url(r'^/?$', 'home'),
	url(r'^configs/?$', 'configs'),
	url(r'^gateways/?$', 'gateways'),
	url(r'^add_gateway/?$', 'add_gateway'),
	url(r'^delete_gateway/(?P<dhcpHost_id>\d+)/?$', 'delete_gateway'),
	url(r'^modify_gateway/(?P<dhcpHost_id>\d+)/?$', 'modify_gateway'),
	url(r'^accept_client/(?P<dhcpHost_id>\d+)/?$', 'accept_client'),
	url(r'^refuse_client/(?P<dhcpHost_id>\d+)/?$', 'refuse_client'),
	url(r'^delete_client/(?P<dhcpHost_id>\d+)/?$', 'delete_client'),
	url(r'^add_config_gateway/?$', 'add_config_gateway'),
	url(r'^add_config_ip/?$', 'add_config_ip'),
	url(r'^delete_config/(?P<dhcpHost_id>\d+)/?$', 'delete_config'),
)
