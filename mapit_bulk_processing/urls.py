from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from .views import (
    HomeView,
    PostcodeFieldView,
    OutputOptionsView,
    PersonalDetailsView,
    PaymentView,
    FinishedView
)

admin.autodiscover()

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(
        r'^(?P<pk>\d+)/postcode-field$',
        PostcodeFieldView.as_view(),
        name='postcode_field'
    ),
    url(
        r'^(?P<pk>\d+)/output-options$',
        OutputOptionsView.as_view(),
        name='output_options'
    ),
    url(
        r'^(?P<pk>\d+)/about-you$',
        PersonalDetailsView.as_view(),
        name='personal_details'
    ),
    url(
        r'^(?P<pk>\d+)/payment$',
        PaymentView.as_view(),
        name='payment'
    ),
    url(
        r'^(?P<pk>\d+)/finished$',
        FinishedView.as_view(),
        name='finished'
    ),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
