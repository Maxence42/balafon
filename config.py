# -*- coding: utf-8 -*-
from sanza.Crm import search_forms, models, forms
from django.utils.translation import ugettext as _

SEARCH_FORMS = [
    (
        _(u'Entity'),
        [
            search_forms.EntityNameSearchForm,
            search_forms.TypeSearchForm,
            search_forms.RelationshipSearchForm,
            search_forms.SectorSearchForm,
            search_forms.RelationshipDateForm,
            search_forms.GroupSearchForm,
            search_forms.NotInGroupSearchForm,
        ],
    ),(
        _(u'Location'),
        [
            search_forms.CitySearchForm,
            search_forms.DepartmentSearchForm,
            search_forms.RegionSearchForm,
            search_forms.CountrySearchForm,
        ],
    ),(
        _(u'Contacts'),
        [
            search_forms.ContactNameSearchForm,
            search_forms.ContactRoleSearchForm,
            search_forms.ContactNewsletterSearchForm,
            search_forms.Contact3rdPartySearchForm,
            search_forms.MainContactSearchForm,
            search_forms.ContactAgeSearchForm,
        ],
    ),(
        _(u'Actions'),
        [
            search_forms.ActionNameSearchForm,
            search_forms.ActionTypeSearchForm,
            search_forms.ActionInProgressForm,
            search_forms.ActionByDoneDate,
            search_forms.ActionByPlannedDate,
            search_forms.ActionByUser,
            
        ],
    ),(
        _(u'Opportunities'),
        [
            search_forms.OpportunityStatusSearchForm,
            search_forms.OpportunityInProgressForm,
            search_forms.OpportunityNameSearchForm,
            search_forms.OpportunityBetween,
            search_forms.OpportunityByStartDate,
            search_forms.OpportunityByEndDate,
            search_forms.OpportunityTypeSearchForm,
            search_forms.OpportunityReminderForm,
            search_forms.NoOpportunityWithNameSearchForm,
            search_forms.NoOpportunityOfTypeSearchForm,
            search_forms.NoOpportunityBetween,
        ],
    ),(
        _(u'Admin'),
        [
            search_forms.ContactsImportSearchForm,
            search_forms.ContactHasEmail,
            search_forms.UnknownContact,
        ],
    ),(
        _(u'Options'),
        [
            search_forms.NoSameAsForm,
        ],
    ),
]

def disable_activity_sector_form():
    for (label, forms) in SEARCH_FORMS:
        if label == _(u'Entity'):
            from sanza.Crm.models import ActivitySector
            if ActivitySector.objects.count() == 0:        
                forms.remove(search_forms.SectorSearchForm)
disable_activity_sector_form()