import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.http.response import HttpResponse, JsonResponse
from dmis_extract.forms import ProtocolForm
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse

from ..models import Protocol
from dmis_extract.lab_db import LabDb


class HomeView(FormView):

    template_name = 'home.html'
    form_class = ProtocolForm

    def __init__(self, *args, **kwargs):
        super(HomeView, self).__init__(*args, **kwargs)
        self.protocol_number = None

    def get_success_url(self):
        return reverse('home')

    def form_invalid(self, form):
        response = super(HomeView, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(HomeView, self).form_valid(form)
        if self.request.is_ajax():
            protocol = self.fetch_protocol(form.data.get('protocol'))
            try:
                data = {'protocol': protocol.identifier, 'protocol_title': protocol.title}
            except AttributeError:
                data = {}
            return JsonResponse(data)
        else:
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            title=settings.PROJECT_TITLE,
            project_name=settings.PROJECT_TITLE,
            protocol_form=ProtocolForm()
        )
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.is_ajax():
            if request.GET.get('action') == 'received-most-recent' and request.GET.get('protocol'):
                db = LabDb(request.GET.get('protocol'), 'BHPLAB')
                df = db.received_condensed(days=5)
                # df.sort_values('modified', inplace=True, ascending=False)
                df.rename(columns={
                    'specimen_condition': 'condition',
                    'drawn_datetime': 'drawn',
                    'received_datetime': 'received',
                    'receive_identifier': 'identifier',
                    'subject_identifier': 'subject',
                    'test_id': 'test'}, inplace=True)
                thead, tbody = db.render_as_table(df, request.GET.get('page', 1))
                response_data = {'thead': thead, 'tbody': tbody}
                return HttpResponse(json.dumps(response_data), content_type='application/json')
        return self.render_to_response(context)

    def fetch_protocol(self, value):
        try:
            protocol = Protocol.objects.get(identifier__iexact=value)
        except Protocol.DoesNotExist:
            protocol = None
        return protocol
