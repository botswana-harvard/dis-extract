from django.conf.urls import url
from django.contrib import admin
# from django.db.utils import OperationalError, ProgrammingError
# from .edc_app_configuration import EdcAppConfiguration

from .views import HomeView, LoginView, LogoutView, LabReportsView

urlpatterns = [
    url(r'^admin/logout/', LogoutView.as_view(url='/login/')),
    url(r'^login/', LoginView.as_view(), name='login_url'),
    url(r'^logout/', LogoutView.as_view(url='/login/'), name='logout_url'),
    url(r'^accounts/login/', LoginView.as_view()),
    url(r'^home/(?P<protocol_identifier>BHP[0-9]{3})/(?P<page>\d+)/',
        HomeView.as_view(), name='home'),
    url(r'^lab-reports/(?P<report_label>\w+)/$',
        LabReportsView.as_view(), name='lab_reports_url'),
    url(r'^home/$', HomeView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'', HomeView.as_view(), name='home'),
]
