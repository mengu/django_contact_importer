from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'django_contact_importer.contacts.views.index', name='contacts_index'),
    url(r'^invite$', 'django_contact_importer.contacts.views.invite', name='invite_contacts'),
)