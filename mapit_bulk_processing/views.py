from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from .models import BulkLookup, StripeCharge
from .forms import PostcodeFieldForm, OutputOptionsForm, PaymentForm


class HomeView(CreateView):
    model = BulkLookup
    fields = ['original_file']
    template_name = 'index.html'

    def get_success_url(self):
        return reverse_lazy('postcode_field', args=[self.object.id])


class PostcodeFieldView(UpdateView):
    model = BulkLookup
    template_name = 'postcode_field.html'
    form_class = PostcodeFieldForm
    context_object_name = 'bulk_lookup'

    def get_form_kwargs(self):
        kwargs = super(PostcodeFieldView, self).get_form_kwargs()
        kwargs['postcode_fields'] = self.object.postcode_field_choices()
        return kwargs

    def get_success_url(self):
        return reverse_lazy('output_options', args=[self.object.id])


class OutputOptionsView(UpdateView):
    model = BulkLookup
    form_class = OutputOptionsForm
    template_name = 'output_options.html'
    context_object_name = 'bulk_lookup'

    def get_success_url(self):
        return reverse_lazy('personal_details', args=[self.object.id])


class PersonalDetailsView(UpdateView):
    model = BulkLookup
    fields = ['email', 'description']
    template_name = 'personal_details.html'
    context_object_name = 'bulk_lookup'

    def get_success_url(self):
        return reverse_lazy('payment', args=[self.object.id])


class PaymentView(CreateView):
    model = StripeCharge
    form_class = PaymentForm
    template_name = 'payment.html'

    def get_success_url(self):
        return reverse_lazy('finished', args=[self.bulk_lookup.id])

    def dispatch(self, request, *args, **kwargs):
        self.bulk_lookup = self.get_bulk_lookup()
        if self.bulk_lookup.paid():
            return HttpResponseRedirect(self.get_success_url())
        return super(PaymentView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(PaymentView, self).get_initial()
        initial['bulk_lookup'] = self.bulk_lookup
        return initial

    def get_bulk_lookup(self):
        return get_object_or_404(
            BulkLookup,
            pk=self.kwargs.get('pk')
        )

    def get_context_data(self, *args, **kwargs):
        context = super(PaymentView, self).get_context_data(*args, **kwargs)
        context['bulk_lookup'] = self.bulk_lookup
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.amount = self.bulk_lookup.price_in_pence()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class FinishedView(DetailView):
    model = BulkLookup
    template_name = 'finished.html'
