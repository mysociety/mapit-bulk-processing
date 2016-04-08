import logging

from django import forms
from django.conf import settings

import stripe
from ukpostcodeutils.validation import is_valid_postcode

from .models import BulkLookup, StripeCharge


logger = logging.getLogger(__name__)


class PostcodeFieldForm(forms.ModelForm):
    # This is hidden by default and only shown if the CSV fails validation
    skip_bad_rows = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=False,
        label="Yes, skip those bad rows"
        )
    postcode_field = forms.ChoiceField(required=True)
    bad_rows = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        postcode_fields = kwargs.pop('postcode_fields')
        super(PostcodeFieldForm, self).__init__(*args, **kwargs)
        self.fields['postcode_field'].choices = postcode_fields

    def clean(self):
        cleaned_data = super(PostcodeFieldForm, self).clean()
        postcode_field = cleaned_data.get('postcode_field')
        skip_bad_rows = cleaned_data.get('skip_bad_rows')
        bad_rows = 0
        bad_row_numbers = []
        for i, row in enumerate(self.instance.original_file_reader()):
            postcode = row[postcode_field].replace(" ", "")
            if not is_valid_postcode(postcode):
                bad_rows += 1
                bad_row_numbers.append(str(i + 1))
        if not skip_bad_rows and bad_rows > 0:
            # Make sure the skip checkbox is shown next time
            self.fields['skip_bad_rows'].widget = forms.CheckboxInput()
            if bad_rows == 1:
                msg = 'Row: '
                msg += ', '.join(bad_row_numbers)
                msg += ' doesn\'t seem to be a valid postcode.'
                msg += ' Do you want us to skip it?'
            else:
                msg = 'Rows: '
                msg += ', '.join(bad_row_numbers)
                msg += ' don\'t seem to be valid postcodes.'
                msg += ' Do you want us to skip them?'
            raise forms.ValidationError(msg)
        else:
            cleaned_data['bad_rows'] = bad_rows
        return cleaned_data

    def save(self, commit=True):
        del self.cleaned_data['skip_bad_rows']
        return super(PostcodeFieldForm, self).save(commit=commit)

    class Meta:
        model = BulkLookup
        fields = ['postcode_field', 'bad_rows']


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
