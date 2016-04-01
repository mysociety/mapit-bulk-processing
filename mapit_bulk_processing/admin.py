from django.contrib import admin
from .models import BulkLookup, OutputOption, StripeCharge


class StripeChargeInline(admin.TabularInline):
    model = StripeCharge


class BulkLookupAdmin(admin.ModelAdmin):
    inlines = [StripeChargeInline]


admin.site.register(BulkLookup, BulkLookupAdmin)
admin.site.register(OutputOption)
admin.site.register(StripeCharge)
