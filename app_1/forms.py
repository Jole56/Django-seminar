from typing import Any, Mapping
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import ModelForm
from django import forms
from django.forms.utils import ErrorList
from .models import Korisnik,Predmeti,Upisi
from django.contrib.auth.hashers import make_password



class FormKorisnik(ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat the Password', widget=forms.PasswordInput)
    class Meta:
        model = Korisnik
        fields = ['first_name','last_name','username','email','role','status']
        help_texts = {
            'username':'(Slova, znamenke i @/./+/_)',
            'status':'(Za profesor ili admin postaviti NONE)'
        }
    # def clean_password(self):
    #     password = make_password(self.cleaned_data.get('password'))
    #     return password
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
class FormEditKorisnik(ModelForm):
    class Meta:
        model = Korisnik
        fields = ['first_name','last_name','username','email','role','status']
        help_texts = {
            'username':'(Slova, znamenke i @/./+/_)',
            'status':'(Za profesor ili admin postaviti NONE)'
        }

class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())



class FormPredmet(forms.ModelForm):
    class Meta:
        model = Predmeti
        fields = ['name','kod','program','sem_red','sem_izv','ects','izborni','nositelj']
        widgets = {
            'name': forms.TextInput(),
            'kod': forms.TextInput(),
            'program': forms.TextInput(),
            'sem_red': forms.NumberInput(),
            'sem_izv': forms.NumberInput(),
            'ects': forms.NumberInput(),
        }

class FormLogout(forms.Form):
    pass


class FormUpisniList(forms.ModelForm):
    class Meta:
        model = Upisi
        fields = ['student','predmet','status']

    
    def __init__(self,*args,**kwargs):
        super(FormUpisniList,self).__init__(*args,**kwargs)
        self.fields['student'].queryset = Korisnik.objects.filter(role='stud')
    
    
class FormAssignNositelj(forms.Form):
    predmeti = forms.ModelChoiceField(queryset=Predmeti.objects.filter(nositelj__isnull=True),label="Predmet")
    nositelj = forms.ModelChoiceField(queryset=Korisnik.objects.filter(role='prof'), label="Nositelj")



class EditStudentStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Upisi.statusi,label='Novi Status')
    