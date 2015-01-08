# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import urllib2

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site
from django.utils.importlib import import_module
from django.utils.timezone import now as dt_now
from django.utils.translation import ugettext as _

from captcha.fields import CaptchaField

from coop_cms.models import Newsletter
from coop_cms.settings import get_newsletter_templates
from coop_cms.utils import dehtml
import floppyforms as forms

from sanza.Crm import settings as crm_settings
from sanza.Crm.models import Group, Contact, Entity, EntityType, Action, ActionType
from sanza.Crm.models import SubscriptionType, Subscription
from sanza.Crm.forms import ModelFormWithCity
from sanza.Crm.widgets import CityAutoComplete
from sanza.Emailing import models
from sanza.Emailing.utils import create_subscription_action, send_notification_email
from sanza.Emailing import settings as emailing_settings


class UnregisterForm(forms.Form):
    reason = forms.CharField(required=False, widget=forms.Textarea, label=_(u"Reason"))


class NewEmailingForm(forms.Form):
    subscription_type = forms.IntegerField(label=_(u"Subscription Type"))
    newsletter = forms.IntegerField(label=_(u"Newsletter"))
    subject = forms.CharField(
        label=_(u"Subject"), required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')})
    )
    contacts = forms.CharField(widget=forms.HiddenInput())
        
    def get_contacts(self):
        ids = self.cleaned_data["contacts"].split(";")
        return models.Contact.objects.filter(id__in=ids)
    
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial')
        initial_contacts = ''
        if initial and initial.has_key('contacts'):
            initial_contacts = u';'.join([unicode(c.id) for c in initial['contacts']])
            initial.pop('contacts')
        super(NewEmailingForm, self).__init__(*args, **kwargs)
        if initial_contacts:
            self.fields['contacts'].initial = initial_contacts
        newsletter_choices = [(0, _(u'-- New --'))] + [(n.id, n.subject) for n in Newsletter.objects.all()]
        self.fields["newsletter"].widget = forms.Select(choices=newsletter_choices)

        subscription_choices = [(n.id, n.name) for n in SubscriptionType.objects.all()]
        self.fields["subscription_type"].widget = forms.Select(choices=subscription_choices)
        
    def clean_subject(self):
        newsletter_id = int(self.cleaned_data['newsletter'])
        subject = self.cleaned_data['subject']
        if newsletter_id == 0 and not subject:
            raise ValidationError(_(u"Please enter a subject for the newsletter"))
        return subject

    def clean_subscription_type(self):
        try:
            subscription_type = int(self.cleaned_data['subscription_type'])
            return SubscriptionType.objects.get(id=subscription_type)
        except (ValueError, KeyError, SubscriptionType.DoesNotExist):
            raise ValidationError(_(u"Please select a valid subscription"))


class NewNewsletterForm(forms.Form):
    subject = forms.CharField(
        label=_(u"Subject"),
        widget=forms.TextInput(attrs={'placeholder': _(u'Subject of the newsletter')})
    )
    template = forms.ChoiceField(label=_(u"Template"), choices=get_newsletter_templates(None, None))
    source_url = forms.URLField(label=_(u'Source URL'), required=False)
    content = forms.CharField(label=_(u'Content'), required=False, widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(NewNewsletterForm, self).__init__(*args, **kwargs)
        
        self.source_content = ""
        
        self.allow_url_sources = getattr(settings, 'SANZA_NEWSLETTER_SOURCES', ())
        if not self.allow_url_sources:
            self.fields['source_url'].widget = forms.HiddenInput()
    
    def clean_source_url(self):
        url = self.cleaned_data['source_url']
        if url:
            #Check in config if the url match with something allowed
            newsletter_sources = getattr(settings, 'SANZA_NEWSLETTER_SOURCES', ())
            for (regex, selector, post_processor) in newsletter_sources:
                if re.match(regex, url):
                    try:
                        #if so get the content
                        html = urllib2.urlopen(url).read()
                        #and extract the selector content as initial content for the newsletter
                        soup = BeautifulSoup(html)
                        content = u''.join([unicode(tag) for tag in soup.select(selector)])
                        if post_processor:
                            #import the post_processor function
                            module_name, processor_name = post_processor.rsplit('.', 1)
                            module = import_module(module_name)
                            post_processor_func = getattr(module, processor_name)
                            #call the post_processor and update the content
                            content = post_processor_func(content)
                        self.source_content = content
                        return url
                    except Exception, msg:
                        raise ValidationError(msg)
            raise ValidationError(_(u"The url is not allowed"))
        return u''

    def clean_content(self):
        url = self.cleaned_data['source_url']
        if url:
            return self.source_content
        return u''


class EmailSubscribeForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': _(u'Email'), 'size': '80'})
    )
    
    class Meta:
        model = Contact
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        self.subscription_type = kwargs.pop('subscription_type', None)
        super(EmailSubscribeForm, self).__init__(*args, **kwargs)
    
    def save(self, request=None):
        contact = super(EmailSubscribeForm, self).save(commit=False)
        
        if crm_settings.ALLOW_SINGLE_CONTACT:
            contact.entity = Entity.objects.create(name=contact.email, type=None, is_single_contact=True)
        else:
            et_id = getattr(settings, 'SANZA_INDIVIDUAL_ENTITY_ID', 1)
            entity_type = EntityType.objects.get(id=et_id)
            contact.entity = Entity.objects.create(name=contact.email, type=entity_type)
        contact.save()
        #delete unknown contacts for the current entity
        contact.entity.contact_set.exclude(id=contact.id).delete()

        queryset = SubscriptionType.objects.filter(sites=Site.objects.get_current())

        form_subscription_type = self.subscription_type
        default_subscription_type = emailing_settings.get_default_subscription_type()
        if not form_subscription_type and default_subscription_type:
            form_subscription_type = default_subscription_type

        if form_subscription_type:
            queryset = queryset.filter(id=form_subscription_type)

        subscriptions = []
        for subscription_type in queryset:
            subscription = Subscription.objects.get_or_create(contact=contact, subscription_type=subscription_type)[0]
            subscription.accept_subscription = True
            subscription.subscription_date = datetime.now()
            subscription.save()
            subscriptions.append(subscription_type.name)
        
        create_subscription_action(contact, subscriptions)
        if subscriptions:
            send_notification_email(request, contact, [], "")
        else:
            send_notification_email(request, contact, [], u"Error: "+_(u"No subscription_type defined"))
                
        return contact


class SubscriptionTypeFormMixin(object):

    def _add_subscription_types_field(self):
        self.fields['subscription_types'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(),
            label='',
            required=False,
            choices=[(st.id, st.name) for st in self.get_queryset()]
        )

    def get_queryset(self):
        return SubscriptionType.objects.filter(sites=Site.objects.get_current())

    def clean_subscription_types(self):
        try:
            subscription_types = [SubscriptionType.objects.get(id=st_id) for st_id in self.cleaned_data['subscription_types']]
        except SubscriptionType.DoesNotExist:
            raise ValidationError(_(u"Invalid subscription type"))
        return subscription_types

    def _save_subscription_types(self, contact):
        subscriptions = []
        for subscription_type in self.get_queryset():

            subscription = Subscription.objects.get_or_create(
                contact=contact,
                subscription_type=subscription_type
            )[0]

            if subscription_type in self.cleaned_data['subscription_types']:
                subscription.accept_subscription = True
                subscription.subscription_date = datetime.now()
                #This is added to the notification email
                subscriptions.append(subscription_type.name)
            else:
                subscription.accept_subscription = False
            subscription.save()
        return subscriptions


class SubscribeForm(ModelFormWithCity, SubscriptionTypeFormMixin):
    city = forms.CharField(
        required=False, label=_(u'City'),
        widget=CityAutoComplete(attrs={'placeholder': _(u'Enter a city'), 'size': '80'})
    )
    entity_type = forms.ChoiceField(required=False, widget=forms.Select())
    entity = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _(u'Name of the entity')})
    )
    groups = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    action_types = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), label='', required=False)
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'placeholder': _(u'Message'), 'cols':'90'}))
    captcha = CaptchaField(help_text=_(u"Make sure you are a human"))

    class Meta:
        model = Contact
        fields = (
            'gender', 'firstname', 'lastname', 'phone', 'mobile', 'email', 'address',
            'address2', 'address3', 'zip_code'
        )
        widgets = {
            #'notes': forms.Textarea(attrs={'placeholder': _(u'Comments'), 'cols':'90'}),
            'lastname': forms.TextInput(attrs={'placeholder': _(u'Lastname'), 'required': 'required'}),
            'firstname': forms.TextInput(attrs={'placeholder': _(u'Firstname')}),
            'phone': forms.TextInput(attrs={'placeholder': _(u'Phone')}),
            'email': forms.TextInput(attrs={'placeholder': _(u'Email'), 'required': 'required'}),
            'zip_code': forms.TextInput(attrs={'placeholder': _(u'zip code')}),
            #'country': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(SubscribeForm, self).__init__(*args, **kwargs)

        self.fields['email'].required = True
        #self.fields['lastname'].required = True
        
        #Do not display (Mrs and M) gender on subscribe form
        self.fields['gender'].choices = self.fields['gender'].choices[:3]

        entity_types_choices = []

        if crm_settings.ALLOW_SINGLE_CONTACT:
            entity_types_choices.append((0, _(u'Individual')))
        else:
            entity_types_choices.append((0, ''))

        entity_types_choices.extend([
            (et.id, et.name) for et in EntityType.objects.filter(subscribe_form=True)
        ])

        self.fields['entity_type'].choices = entity_types_choices

        self.fields['groups'].choices = [
            (g.id, g.name) for g in Group.objects.filter(subscribe_form=True)
        ]
        
        self.fields['action_types'].choices = [
            (at.id, at.name) for at in ActionType.objects.filter(subscribe_form=True)
        ]
        
        self._add_subscription_types_field()
    
    def clean_entity_type(self):
        try:
            entity_type = int(self.cleaned_data['entity_type'])
            if entity_type:
                return EntityType.objects.get(id=entity_type)
            return None
        except (ValueError, EntityType.DoesNotExist):
            raise ValidationError(_(u"Invalid entity type"))
        
    def get_entity(self):
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self.cleaned_data['entity']
        if entity_type:
            if entity:
                return Entity.objects.create(name=entity, type=entity_type)
        else:
            if crm_settings.ALLOW_SINGLE_CONTACT:
                return Entity.objects.create(name=entity, type=None, is_single_contact=True)
            else:
                et_id = getattr(settings, 'SANZA_INDIVIDUAL_ENTITY_ID', 1)
                entity_type = EntityType.objects.get(id=et_id)
                entity_name = u"{0} {1}".format(
                    self.cleaned_data['lastname'], self.cleaned_data['firstname'])
                return Entity.objects.create(name=entity_name, type=entity_type)
            
    def clean_entity(self):
        entity_type = self.cleaned_data.get('entity_type', None)
        entity = self._dehtmled_field("entity")
        if entity_type:
            if not entity:
                raise ValidationError(_(u"{0}: Please enter a name".format(entity_type)))
        else:
            data = [self.cleaned_data[x] for x in ('lastname', 'firstname')]
            entity = u' '.join([x for x in data if x]).strip().upper()
            
        return entity
         
    def _dehtmled_field(self, fieldname, **kwargs):
        value = self.cleaned_data[fieldname]
        return dehtml(value, **kwargs)
        
    def clean_lastname(self):
        return self._dehtmled_field("lastname")
    
    def clean_firstname(self):
        return self._dehtmled_field("firstname")
    
    def clean_phone(self):
        return self._dehtmled_field("phone")
    
    def clean_mobile(self):
        return self._dehtmled_field("mobile")
    
    def clean_address(self):
        return self._dehtmled_field("address")
    
    def clean_address2(self):
        return self._dehtmled_field("address2")
    
    def clean_address3(self):
        return self._dehtmled_field("address3")
    
    def clean_message(self):
        message = self._dehtmled_field("message", allow_spaces=True)
        if len(message) > 10000:
            raise ValidationError(_(u"Your message is too long"))
        return message
    
    def clean_groups(self):
        try:
            groups = [Group.objects.get(id=group_id) for group_id in self.cleaned_data['groups']]
        except Group.DoesNotExist:
            raise ValidationError(_(u"Invalid group"))
        return groups
    
    def clean_action_types(self):
        try:
            action_types = [ActionType.objects.get(id=at_id) for at_id in self.cleaned_data['action_types']]
        except ActionType.DoesNotExist:
            raise ValidationError(_(u"Invalid action type"))
        return action_types

    def save(self, request=None):
        contact = super(SubscribeForm, self).save(commit=False)
        contact.entity = self.get_entity()
        contact.city = self.cleaned_data['city']
        contact.save()
        #delete unknown contacts for the current entity
        contact.entity.contact_set.filter(lastname='', firstname='').exclude(id=contact.id).delete()
        
        #force also the city on the entity
        contact.entity.city = contact.city
        
        groups = self.cleaned_data['groups']
        for g in groups:
            contact.entity.group_set.add(g)
        contact.entity.save()
        
        subscriptions = self._save_subscription_types(contact)
        
        message = self.cleaned_data["message"]

        if message:
            action_type = ActionType.objects.get_or_create(name=_(u"Message"))[0]
            action = Action.objects.create(
                subject=_(u"Message from web site"),
                type=action_type,
                planned_date=datetime.now(),
                detail=message,
                display_on_board=True
            )
            action.contacts.add(contact)
            action.save()
        
        if subscriptions:
            create_subscription_action(contact, subscriptions)
        
        action_types = self.cleaned_data['action_types']
        actions = []
        for action_type in action_types:
            action = Action.objects.create(
                subject=_(u"Contact"),
                type=action_type,
                planned_date=datetime.now(),
                display_on_board=True
            )
            action.contacts.add(contact)
            action.save()
            actions.append(action)
            
        #send an email
        send_notification_email(request, contact, actions, message)
        
        return contact


class NewsletterSchedulingForm(forms.ModelForm):
    class Meta:
        model = models.Emailing
        fields = ('scheduling_dt',)

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = {'scheduling_dt': dt_now() + timedelta(minutes=5)}
        super(NewsletterSchedulingForm, self).__init__(*args, **kwargs)

    def clean_scheduling_dt(self):
        sch_dt = self.cleaned_data['scheduling_dt']

        if not sch_dt:
            raise ValidationError(_(u"This field is required"))

        if sch_dt < dt_now():
            raise ValidationError(_(u"The scheduling date must be in future"))

        return sch_dt
