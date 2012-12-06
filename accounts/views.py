from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from accounts.forms import UserCreationForm, ProfileChangeForm
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

#temp
from django.shortcuts import render

@csrf_protect
@sensitive_post_parameters()
def signup(request, template_name='accounts/signup.html', signup_form=UserCreationForm, post_signup_redirect="/accounts/login/"):
    if request.user.is_authenticated():
	    return HttpResponseRedirect('/')
    if request.method == "POST":
        form = signup_form(request.POST)
        if form.is_valid():
	    form.save()
            return HttpResponseRedirect(post_signup_redirect)
    else:
        form = signup_form()
    return render_to_response(template_name, {'form': form,}, context_instance=RequestContext(request))

@login_required
def profile(request, template_name='accounts/profile.html'):
    return render(request, template_name)


@sensitive_post_parameters()
@csrf_protect
@login_required
def profile_change(request,
                   template_name='accounts/profile_change_form.html',
                   post_change_redirect='/accounts/profile/',
                   profile_change_form=ProfileChangeForm):
    if request.method == "POST":
	form = profile_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
	    form = profile_change_form(user=request.user, initial={'new_email': request.user.email})
    return TemplateResponse(request, template_name, {'form': form,})
