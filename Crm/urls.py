# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('sanza.Crm.views',
    url(r'^entities$', 'view_entities_list', name='crm_view_entities_list'),
    url(r'^entity/(?P<entity_id>\d+)$', 'view_entity', name='crm_view_entity'),
    url(r'^edit-entity/(?P<entity_id>\d+)$', 'edit_entity', name='crm_edit_entity'),
    url(r'^create-entity$', 'create_entity', name='crm_create_entity'),
    url(r'^delete-entity/(?P<entity_id>\d+)$', 'delete_entity', name='crm_delete_entity'),
    url(r'^add-contact/(?P<entity_id>\d+)$', 'add_contact', name='crm_add_contact'),
    url(r'^delete-contact/(?P<contact_id>\d+)$', 'delete_contact', name='crm_delete_contact'),
    url(r'^edit-contact/(?P<contact_id>\d+)$', 'edit_contact', name='crm_edit_contact'),
    url(r'^edit-contact-advanced/(?P<contact_id>\d+)$', 'edit_contact', kwargs={'mini': False}, name='crm_edit_contact_advanced'),
    url(r'^edit-contact-on-create-entity/(?P<contact_id>\d+)$', 'edit_contact', kwargs={'go_to_entity': True}, name='crm_edit_contact_after_entity_created'),
    url(r'^view-contact/(?P<contact_id>\d+)$', 'view_contact', name='crm_view_contact'),
    url(r'^same-as/(?P<contact_id>\d+)$', 'same_as', name='crm_same_as'),
    url(r'^add-entity-to-group/(?P<entity_id>\d+)$', 'add_entity_to_group', name='crm_add_entity_to_group'),
    url(r'^add-contact-to-group/(?P<contact_id>\d+)$', 'add_contact_to_group', name='crm_add_contact_to_group'),
    url(r'^get-group-suggest-list$', 'get_group_suggest_list', name='crm_get_group_suggest_list'),
    url(r'^remove-from-group/(?P<group_id>\d+)/(?P<entity_id>\d+)$', 'remove_entity_from_group', name='crm_remove_entity_from_group'),
    url(r'^remove-contact-from-group/(?P<group_id>\d+)/(?P<contact_id>\d+)$', 'remove_contact_from_group', name='crm_remove_contact_from_group'),
    url(r'^group-members/(?P<group_id>\d+)$', 'get_group_members', name='crm_get_group_members'),
    url(r'^edit-group/(?P<group_id>\d+)$', 'edit_group', name='crm_edit_group'),
    url(r'^delete-group/(?P<group_id>\d+)$', 'delete_group', name='crm_delete_group'),
    url(r'^add-group$', 'add_group', name='crm_add_group'),
    url(r'^my-groups$', 'see_my_groups', name='crm_see_my_groups'),
    url(r'^city-name/(?P<city>.*)$', 'get_city_name', name='crm_get_city_name'),
    url(r'^cities/list$', 'get_cities', name='crm_get_cities'),
    url(r'^board$', 'view_board_panel', name='crm_board_panel'),
    url(r'^add-action-for-entity/(?P<entity_id>\d+)$', 'add_action_for_entity', name='crm_add_action_for_entity'),
    url(r'^edit-action/(?P<action_id>\d+)$', 'edit_action', name='crm_edit_action'),
    url(r'^do-action/(?P<action_id>\d+)$', 'do_action', name='crm_do_action'),
    url(r'^delete-action/(?P<action_id>\d+)$', 'delete_action', name='crm_delete_action'),
    url(r'^actions/(?P<entity_id>\d+)$', 'view_entity_actions', name='crm_entity_actions'),
    url(r'^add-opportunity/(?P<entity_id>\d+)$', 'add_opportunity_for_entity', name='crm_add_opportunity_for_entity'),
    url(r'^edit-opportunity/(?P<opportunity_id>\d+)$', 'edit_opportunity', name='crm_edit_opportunity'),
    url(r'^view-opportunity/(?P<opportunity_id>\d+)$', 'view_opportunity', name='crm_view_opportunity'),
    url(r'^delete-opportunity/(?P<opportunity_id>\d+)$', 'delete_opportunity', name='crm_delete_opportunity'),
    url(r'^opportunities/(?P<entity_id>\d+)$', 'view_entity_opportunities', name='crm_entity_opportunities'),
    url(r'^opportunities/$', 'view_all_opportunities', name='crm_all_opportunities'),
    url(r'^opportunities-by/(?P<ordering>.+)$', 'view_all_opportunities', name='crm_all_opportunities_by'),
    url(r'^add-opportunity/$', 'add_opportunity', name='crm_add_opportunity'),
    url(r'^add-action/$', 'add_action', name='crm_add_action'),
    url(r'^opportunity-name/(?P<opp_id>\d+)$', 'get_opportunity_name', name='crm_get_opportunity_name'),
    url(r'^opportunities/list$', 'get_opportunities', name='crm_get_opportunities'),
    url(r'^mailto-opportunity-contacts/(?P<opportunity_id>\d+)$', 'mailto_opportunity_contacts', name='crm_mailto_opportunity_contacts'),
    url(r'^entity-name/(?P<entity_id>.+)$', 'get_entity_name', name='crm_get_entity_name'),
    url(r'^entities/list$', 'get_entities', name='crm_get_entities'),
    url(r'^all-actions$', 'view_all_actions', name='crm_all_actions'),
    url(r'^edit-custom-fields/(?P<model_name>\w+)/(?P<instance_id>\d+)$', 'edit_custom_fields', name='crm_edit_custom_fields'),
    url(r'^contacts-import/new$', 'new_contacts_import', name='crm_new_contacts_import'),
    url(r'^contacts-import/(?P<import_id>\d+)$', 'confirm_contacts_import', name='crm_confirm_contacts_import'),
    url(r'^contacts-import/template.csv$', 'contacts_import_template', name='crm_contacts_import_template'),
    url(r'^group-name/(?P<gr_id>\d+)$', 'get_group_name', name='crm_get_group_name'),
    url(r'^groups/list$', 'get_groups', name='crm_get_groups'),
)