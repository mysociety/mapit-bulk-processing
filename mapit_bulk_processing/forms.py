import logging

from django import forms
from django.conf import settings

import stripe

from .models import BulkLookup, StripeCharge


logger = logging.getLogger(__name__)


class PostcodeFieldForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        postcode_fields = kwargs.pop('postcode_fields')
        super(PostcodeFieldForm, self).__init__(*args, **kwargs)
        self.fields['postcode_field'] = forms.ChoiceField(
            choices=postcode_fields,
            required=True
        )

    class Meta:
        model = BulkLookup
        fields = ['postcode_field']


class OutputOptionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OutputOptionsForm, self).__init__(*args, **kwargs)
        self.fields['output_options'].required = True

    class Meta:
        model = BulkLookup
        fields = ['output_options']
        widgets = {
            'output_options': forms.CheckboxSelectMultiple
        }


class PaymentForm(forms.ModelForm):
    def clean(self):
        """
        Validate everything by trying to charge the card with Stripe
        """
        super(PaymentForm, self).clean()
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        token = self.cleaned_data['stripeToken']
        bulk_lookup = self.cleaned_data['bulk_lookup']
        try:
            self.charge_card(bulk_lookup, token)
        except stripe.CardError, e:
            # The card has been declined
            logger.exception(e)
            raise forms.ValidationError(
                """
                Sorry, your card has been declined.
                Perhaps you can try another?
                """
            )

    def charge_card(self, bulk_lookup, token):
        stripe.Charge.create(
            amount=bulk_lookup.price_in_pence(),
            currency="gbp",
            source=token,
            description=bulk_lookup.__str__(),
            metadata={"bulk_lookup_id": bulk_lookup.id}
        )

    class Meta:
        model = StripeCharge
        fields = ['stripeToken', 'bulk_lookup']
        widgets = {
            'stripeToken': forms.HiddenInput(),
            'bulk_lookup': forms.HiddenInput()
        }
