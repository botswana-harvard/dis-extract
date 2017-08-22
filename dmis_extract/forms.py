from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder, Button
from django.core.urlresolvers import reverse


class LoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'id-login-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))


class ProtocolForm(forms.Form):

    protocol = forms.CharField(
        label="BHP Protocol Number ")

    def __init__(self, *args, **kwargs):
        super(ProtocolForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-protocol-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('home')
        self.helper.add_input(Submit('submit', 'Submit'))


class BillingReportForm(forms.Form):

    protocol = forms.CharField(
        label="BHP Protocol Number ",
        required=False,
        help_text="Leave blank for 'all'")

    start_date = forms.CharField(
        label="Start date")

    end_date = forms.CharField(
        label="End date")

    tid = forms.CharField(
        label="Test Group",
        required=False,
        help_text="Leave blank for 'all'")

    def __init__(self, *args, **kwargs):
        super(BillingReportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-billing-report-form'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('lab_reports_url', kwargs={'report_label': 'billing'})
        self.helper.html5_required = True
        self.helper.layout = Layout(
            *['start_date', 'end_date', 'protocol', 'tid'],
            ButtonHolder(
                Button('cancel-log-entry', 'Cancel'),
                Submit('submit-log-entry', 'Save', css_class="pull-right"),
            ))
