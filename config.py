# -*- coding: utf-8 -*-
from sanza.Crm import search_forms, models, forms
from django.utils.translation import ugettext as _

SEARCH_FORMS = [
    (
        _(u'Entity'),
        (
            search_forms.EntityNameSearchForm,
            search_forms.TypeSearchForm,
            search_forms.RelationshipSearchForm,
            search_forms.RelationshipDateForm,
            search_forms.SectorSearchForm,
            search_forms.GroupSearchForm,
        ),
    ),(
        _(u'Location'),
        (
            search_forms.CitySearchForm,
            search_forms.DepartmentSearchForm,
            search_forms.RegionSearchForm,
            search_forms.CountrySearchForm,
        ),
    ),(
        _(u'Contacts'),
        (
            search_forms.ContactNameSearchForm,
            search_forms.ContactRoleSearchForm,
            search_forms.ContactNewsletterSearchForm,
            search_forms.Contact3rdPartySearchForm,
            search_forms.MainContactSearchForm,
            search_forms.ContactAgeSearchForm,
        )
    ),(
        _(u'Actions'),
        (
            search_forms.ActionNameSearchForm,
            search_forms.ActionTypeSearchForm,
            search_forms.ActionInProgressForm,
            search_forms.ActionByDoneDate,
            search_forms.ActionByPlannedDate,
            search_forms.ActionByUser,
            
        ),
    ),(
        _(u'Opportunities'),
        (
            search_forms.OpportunityStatusSearchForm,
            search_forms.OpportunityInProgressForm,
            search_forms.OpportunityNameSearchForm,
            search_forms.OpportunityByStartDate,
            search_forms.OpportunityByEndDate,
            search_forms.OpportunityTypeSearchForm,
            search_forms.OpportunityReminderForm,
        ),
    ),(
        _(u'Options'),
        (
            search_forms.NoSameAsForm,
        ),
    ),
]