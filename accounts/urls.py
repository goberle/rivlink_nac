from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'accounts/login.html'}),
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'accounts/signup.html','next_page': '/'}),
	url(r'^signup/$', 'accounts.views.signup', {'template_name': 'accounts/signup.html'}),
	url(r'^password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'accounts/password_reset_form.html', 'email_template_name': 'accounts/password_reset_email.html'}),
	url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'accounts/password_reset_done.html'}),
	url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'accounts/password_reset_confirm.html','post_reset_redirect': '/accounts/login/'}),
	url(r'profile/$', 'accounts.views.profile_change'),
) 
