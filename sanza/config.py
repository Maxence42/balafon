# -*- coding: utf-8 -*-
from sanza.Crm import search_forms, models, forms
from django.utils.translation import ugettext as _

SEARCH_FORMS = [
    (
        _(u'Entity'),
        [
            search_forms.EntityNameSearchForm,
            search_forms.EntityNameStartsWithSearchForm,
            search_forms.TypeSearchForm,
            search_forms.RelationshipDateForm,
         ],
    ),(
        _(u'Group'),
        [
            search_forms.GroupSearchForm,
            search_forms.GroupSearchFormDropdownWidget,
            search_forms.NotInGroupSearchForm,
        ],
    ),(
        _(u'Location'),
        [
            search_forms.CitySearchForm,
            search_forms.DepartmentSearchForm,
            search_forms.RegionSearchForm,
            search_forms.CountrySearchForm,
            search_forms.ZipCodeSearchForm,
            search_forms.HasZipCodeForm,
        ],
    ),(
        _(u'Contacts'),
        [
            search_forms.ContactNameSearchForm,
            search_forms.ContactRoleSearchForm,
            search_forms.ContactNewsletterSearchForm,
            search_forms.Contact3rdPartySearchForm,
            search_forms.SecondarySearchForm,
            search_forms.ContactAgeSearchForm,
            #search_forms.ContactOpportunityStatusSearchForm,
            #search_forms.ContactOpportunityNameSearchForm,
            #search_forms.ContactNoOpportunityWithNameSearchForm,
            #search_forms.ContactOpportunityByEndDate,
            #search_forms.ContactOpportunityByStartDate,
            #search_forms.ContactNoOpportunityBetween,
            #search_forms.ContactOpportunityTypeSearchForm,
            #search_forms.ContactNoOpportunityOfTypeSearchForm,
            #search_forms.ContactOpportunityInProgressForm,
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
            search_forms.ActionStatus,
            search_forms.ActionLtAmount,
            search_forms.ActionGteAmount,
        ],
    ),(
        _(u'Opportunities'),
        [
            search_forms.OpportunityStatusSearchForm,
            search_forms.OpportunitySearchForm,
            search_forms.NotInOpportunitySearchForm,
            #search_forms.OpportunityInProgressForm,
            search_forms.OpportunityNameSearchForm,
            #search_forms.OpportunityBetween,
            #search_forms.OpportunityByStartDate,
            #search_forms.OpportunityByEndDate,
            search_forms.OpportunityTypeSearchForm,
            search_forms.OpportunityReminderForm,
            #search_forms.NoOpportunityWithNameSearchForm,
            #search_forms.NoOpportunityOfTypeSearchForm,
            #search_forms.NoOpportunityBetween,
        ],
    ),(
        _(u'Admin'),
        [
            search_forms.ContactsImportSearchForm,
            search_forms.ContactHasEmail,
            search_forms.ContactHasPersonalEmail,
            search_forms.UnknownContact,
            search_forms.ContactsAndEntitiesByChangeDate,
            search_forms.ContactsByCreationDate,
            search_forms.ContactsByUpdateDate,
            search_forms.EntitiesByCreationDate,
            search_forms.EntitiesByUpdateDate,
        ],
    ),(
        _(u'Options'),
        [
            search_forms.NoSameAsForm,
        ],
    ),
]