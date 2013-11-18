from django.conf.urls import patterns, url

urlpatterns = patterns('dhcpHost.views',
	url(r'^/?$', 'home'),
	url(r'^hosts/?$', 'hosts'),
	url(r'^gateways/?$', 'gateways'),
	url(r'^add_gateway/?$', 'add_gateway'),
	url(r'^add_host/?$', 'add_host'),
	url(r'^delete_gateway/(?P<gw_id>(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}))/?$', 'delete_gateway'),
	url(r'^accept_client/(?P<dhcpHost_id>\d+)/?$', 'accept_client'),
	url(r'^refuse_client/(?P<dhcpHost_id>\d+)/?$', 'refuse_client'),
	url(r'^delete_client/(?P<dhcpHost_id>\d+)/?$', 'delete_client'),
	url(r'^delete_host/(?P<dhcpHost_id>\d+)/?$', 'delete_host'),
)
