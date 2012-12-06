# -*- coding: Utf-8 -*-
from django.contrib.auth.models import User
from django import forms

class UserCreationForm(forms.ModelForm):
    username = forms.RegexField(label="Nom d'utilisateur", max_length=30, regex=r'^\w+$', 
		                error_messages = {'invalid': "Le nom d'utilisateur ne peut contenir que des lettres et des chiffres."})
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput)
    email1 = forms.EmailField(label="Email", max_length=75)
    email2 = forms.EmailField(label="Confirmer l'email", max_length=75)

    class Meta:
        model = User
        fields = ("username","first_name","last_name",)

    def clean_username(self):
	username = self.cleaned_data["username"]
	users_found = User.objects.filter(username__iexact=username)
	if len(users_found) >= 1:
	    raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
	return self.cleaned_data["username"]

    def clean_first_name(self):
	first_name = self.cleaned_data.get("first_name", "")
	if len(first_name) == 0:
	    raise forms.ValidationError("Ce champ est obligatoire.")
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
	last_name = self.cleaned_data.get("last_name", "")
	if len(last_name) == 0:
	    raise forms.ValidationError("Ce champ est obligatoire.")
        return self.cleaned_data["last_name"]

    def clean_password(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2
    
    def clean_email1(self):
        email1 = self.cleaned_data["email1"]
        users_found = User.objects.filter(email__iexact=email1)
        if len(users_found) >= 1:
            raise forms.ValidationError("Un autre utilisateur possède déjà cette adresse email.")
        return email1

    def clean_email2(self):
        email1 = self.cleaned_data.get("email1", "")
        email2 = self.cleaned_data["email2"]
        if email1 != email2:
            raise forms.ValidationError("Les deux adresses email ne correspondent pas.")
        return email2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email1"]
        user.is_active = True
        if commit:
            user.save()
        return user

class ProfileChangeForm(forms.Form):
    new_email = forms.EmailField(label="Email", max_length=75)
    new_password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ProfileChangeForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
            	raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
	if self.cleaned_data['new_password1']:
	    self.user.set_password(self.cleaned_data['new_password1'])

	self.user.email = self.cleaned_data['new_email']

        if commit:
            self.user.save()
        return self.user
