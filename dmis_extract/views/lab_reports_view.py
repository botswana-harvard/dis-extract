from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from dmis_extract.forms import BillingReportForm


class LabReportsView(FormView):

    template_name = 'home.html'
    form_class = BillingReportForm

    def get_success_url(self):
        return reverse('lab_reports_url', kwargs={'report_label': 'billing'})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LabReportsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.kwargs)
        context.update(
            title=settings.PROJECT_TITLE,
            project_name=settings.PROJECT_TITLE,
            billing_report_form=BillingReportForm(
                initial={
                    'start_date': date.today() + relativedelta(day=1),
                    'end_date': date.today() + relativedelta(day=1, months=+1, days=-1)
                }),
        )
        return context
