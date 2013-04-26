# -*- coding: utf-8 -*-

import floppyforms as forms
from sanza.Crm.forms import ModelFormWithCity
from sanza.Crm.widgets import CityAutoComplete
from sanza.Crm.models import Contact
from django.utils.translation import ugettext_lazy as _
#from registration.forms import RegistrationForm
from django.contrib.auth.models import User

class ProfileForm(ModelFormWithCity):
    
    city = forms.CharField(
        required = False, label=_(u'City'),   
        widget = CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    
    class Media:
        css = {
             'all': ('css/base/jquery-ui-1.9.2.css',),
        }
        js = ('js/jquery-ui-1.9.2.js',)
    
    class Meta:
        model = Contact
        exclude=('uuid', 'same_as', 'imported_by', 'entity')
        fields = (
            'gender', 'lastname', 'firstname', 'birth_date', 'email', 'phone', 'mobile',
            'address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country',
            'accept_newsletter', 'accept_3rdparty',
            #'photo'
        )
        
        fieldsets = [
            ('name', {'fields': ['gender', 'lastname', 'firstname', 'birth_date'], 'legend': _(u'Name')}),
            ('web', {'fields': ['email', 'phone', 'mobile'], 'legend': _(u'Phone / Web')}),
            ('address', {'fields': ['address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country'], 'legend': _(u'Address')}),
            ('relationship', {'fields': ['accept_newsletter', 'accept_3rdparty'], 'legend': _(u'Relationship')}),
            #('photo', {'fields': ['photo'], 'legend': _(u'Photo')}),
        ]
        

class Email(forms.EmailField): 
    def clean(self, value):
        super(Email, self).clean(value)
        if User.objects.filter(email=value).count() > 0:
            raise forms.ValidationError(
                _(u"This email is already registered. Use the 'forgot password' link on the login page")
            )
        return value
        
class UserRegistrationForm(forms.Form):
    email = Email(required=True, label=_(u"Email"), widget=forms.TextInput())
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Password"))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Repeat your password"))
    accept_termofuse = forms.BooleanField(label=_(u'Accept term of use'))
    accept_newsletter = forms.BooleanField(label=_(u'Accept newsletter'), required=False)
    accept_3rdparty = forms.BooleanField(label=_(u'Accept 3rd party'), required=False)
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        
        for (name, field) in self.fields.items():
            field.widget.attrs['placeholder'] = field.label
            if not (name.find('accept')==0):
                field.widget.attrs['required'] = "required"
        
    def clean(self, *args, **kwargs):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError(_(u'Passwords are not the same'))
        return super(UserRegistrationForm, self).clean(*args, **kwargs)
        
class MessageForm(forms.Form):
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={
        'placeholder': _(u"Your message"),
    }))
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message)>10000:
            raise forms.ValidationError(_(u'Message is too long'))
        return message