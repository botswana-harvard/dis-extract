from django.urls.conf import path, re_path
from django.contrib import admin
# from django.db.utils import OperationalError, ProgrammingError
# from .edc_app_configuration import EdcAppConfiguration

from .views import HomeView, LoginView, LogoutView, LabReportsView

urlpatterns = [
    path('admin/logout/', LogoutView.as_view(url='/login/')),
    path('login/', LoginView.as_view(), name='login_url'),
    path('logout/', LogoutView.as_view(url='/login/'), name='logout_url'),
    path('accounts/login/', LoginView.as_view()),
    re_path('home/(?P<protocol_identifier>BHP[0-9]{3})/(?P<page>\d+)/',
            HomeView.as_view(), name='home'),
    re_path('lab-reports/(?P<report_label>\w+)/$',
            LabReportsView.as_view(), name='lab_reports_url'),
    path('home/', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
]
