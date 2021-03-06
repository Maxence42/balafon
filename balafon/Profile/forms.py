# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms
from registration import get_version as get_registration_version

from balafon.Crm.models import Contact, EntityType
from balafon.Crm.forms import ModelFormWithCity
from balafon.Crm.widgets import CityAutoComplete
from balafon.Emailing.forms import SubscriptionTypeFormMixin
from balafon.Profile.models import ContactProfile
from balafon.settings import has_entity_on_registration_form, get_registration_accept_terms_of_use_link


class ProfileForm(ModelFormWithCity, SubscriptionTypeFormMixin):
    
    city = forms.CharField(
        required=False,
        label=_(u'City'),
        widget=CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )

    class Media:
        css = {
            'all': ('css/base/jquery-ui-1.9.2.css',),
        }
        js = ('js/jquery-ui-1.9.2.js',)
    
    class Meta:
        model = Contact
        fields = (
            'gender', 'lastname', 'firstname', 'birth_date', 'email', 'phone', 'mobile',
            'address', 'address2', 'address3', 'zip_code', 'city', 'cedex', 'country',
            'accept_notifications',
        )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self._add_subscription_types_field(contact=self.instance)


class EmailField(forms.EmailField):

    def clean(self, value):
        super(EmailField, self).clean(value)
        if User.objects.filter(email__iexact=value).count() > 0:
            raise forms.ValidationError(
                _(u"This email is already registered. Use the 'forgot password' link on the login page")
            )
        return value


class UserRegistrationForm(ModelFormWithCity, SubscriptionTypeFormMixin):
    email = EmailField(required=True, label=_(u"Email"), widget=forms.TextInput())
    password1 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Password"))
    password2 = forms.CharField(required=True, widget=forms.PasswordInput(), label=_(u"Repeat your password"))

    entity_type = forms.ChoiceField(required=False, widget=forms.Select())
    entity = forms.CharField(
         required=False,
         widget=forms.TextInput(attrs={'placeholder': _(u'Name of the entity')})
    )

    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)

    accept_termofuse = forms.BooleanField(
        label=_(u'Accept terms of use'),
        help_text=_(u"Check for accepting the terms of use")
    )

    city = forms.CharField(
        required=False,
        label=_(u'City'),
        widget=CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )

    class Meta:
        model = ContactProfile
        fields = (
            'email', 'password1', 'password2', 'entity_type', 'entity', 'gender', 'firstname', 'lastname',
            'phone', 'mobile', 'address',
            'zip_code', 'city', 'cedex', 'country', 'groups', 'accept_termofuse'
        )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        if 'gender' in self.fields:
            # do not display Mrs and Mr
            self.fields['gender'].choices = ((0, u'----------'), ) + Contact.GENDER_CHOICE[:2]

        if 'entity_type' in self.fields:
            self.fields['entity_type'].choices = [(0, _(u'Individual'))]+[
                (et.id, et.name) for et in EntityType.objects.filter(subscribe_form=True)
            ]
        if not has_entity_on_registration_form():
            self.fields['entity_type'].inital = 0
            self.fields['entity_type'].widget = forms.HiddenInput()
            self.fields['entity'].widget = forms.HiddenInput()

        termsofuse_url = get_registration_accept_terms_of_use_link()
        if 'accept_termofuse' in self.fields and termsofuse_url:
            self.fields['accept_termofuse'].label = mark_safe(
                ugettext(u'Accept <a href="{0}">terms of use</a>').format(
                    termsofuse_url
                )
            )

        self._add_subscription_types_field()

    def clean_entity(self, ):
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self.cleaned_data['entity']
        if entity_type:
            if not entity:
                raise ValidationError(_(u"{0}: Please enter a name".format(entity_type)))
        return entity
        
    def clean_entity_type(self):
        try:
            entity_type_id = int(self.cleaned_data['entity_type'] or 0)
        except ValueError:
            raise ValidationError(ugettext(u'Invalid entity type'))
       
        if entity_type_id:
            try:
                return EntityType.objects.get(id=entity_type_id)
            except EntityType.DoesNotExist:
                raise ValidationError(ugettext(u'Unknown entity type'))
        
        return None

    def clean(self, *args, **kwargs):
        password1 = self.cleaned_data.get('password1', "")
        password2 = self.cleaned_data.get('password2', "")
        if password1 and (password1 != password2):
            raise forms.ValidationError(_(u'Passwords are not the same'))
        return super(UserRegistrationForm, self).clean(*args, **kwargs)

    def save(self, commit=True):

        if get_registration_version() >= "2.0.0":
            # Django registration 2.0
            # The registration form should return a user

            email = self.cleaned_data["email"]
            username = email[:30]

            user = User.objects.create(
                username=username, email=email, is_active=False
            )
            password = self.cleaned_data.get('password1', "")
            user.set_password(password)

            return user
        else:
            # Django registration 1.0
            return super(UserRegistrationForm, self).save(commit)


class MinimalUserRegistrationForm(UserRegistrationForm):

    class Meta:
        model = ContactProfile
        fields = (
            'email', 'password1', 'password2', 'firstname', 'lastname', 'accept_termofuse',
            'zip_code', 'city', 'country', 'groups_ids',
        )

    def __init__(self, *args, **kwargs):
        super(MinimalUserRegistrationForm, self).__init__(*args, **kwargs)
        for hidden_field in ('entity', 'entity_type', 'zip_code', 'city', 'country', 'groups_ids'):
            self.fields[hidden_field].widget = forms.HiddenInput()

        for required_field in ('firstname', 'lastname'):
            self.fields[required_field].required = True


class MessageForm(forms.Form):
    message = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': _(u"Your message"),})
    )
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) > 10000:
            raise forms.ValidationError(_(u'Message is too long'))
        return message