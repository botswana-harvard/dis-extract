import json

from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import FormView

from ..forms import ProtocolForm, BillingReportForm
from ..lab_data import LabData
from ..models import Protocol


class HomeView(FormView):

    template_name = 'home.html'
    form_class = ProtocolForm
    protocol_form_cls = ProtocolForm
    billing_report_form_cls = BillingReportForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol_number = None

    def get_success_url(self):
        return reverse('home')

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            protocol = self.fetch_protocol(form.data.get('protocol'))
            try:
                data = {'protocol': protocol.identifier,
                        'protocol_title': protocol.title}
            except AttributeError:
                data = {'protocol': '', 'protocol_title': ''}
            return JsonResponse(data)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=settings.PROJECT_TITLE,
            project_name=settings.PROJECT_TITLE,
            protocol_form=self.protocol_form_cls(),
            billing_report_form=self.billing_report_form_cls(
                initial={
                    'start_date': date.today() + relativedelta(day=1),
                    'end_date': date.today() + relativedelta(day=1, months=+1, days=-1)
                }),
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            if request.GET.get('action') == 'received-most-recent' and request.GET.get('protocol'):
                db = LabData(
                    protocol_identifier=request.GET.get('protocol'),
                    database='BHPLAB')
                df = db.received_condensed(days=5)
                df = df.sort_values('modified', ascending=False)
                df.rename(columns={
                    'specimen_condition': 'condition',
                    'drawn_datetime': 'drawn',
                    'received_datetime': 'received',
                    'receive_identifier': 'identifier',
                    'subject_identifier': 'subject',
                    'test_id': 'test'}, inplace=True)
                thead, tbody = db.render_as_table(
                    df, request.GET.get('page', 1))
                response_data = {'thead': thead, 'tbody': tbody}
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    def fetch_protocol(self, value):
        try:
            protocol = Protocol.objects.get(identifier__iexact=value)
        except Protocol.DoesNotExist:
            protocol = None
        return protocol
