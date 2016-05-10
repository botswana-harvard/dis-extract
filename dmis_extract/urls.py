"""bcpp_interview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
# from django.db.utils import OperationalError, ProgrammingError
# from .edc_app_configuration import EdcAppConfiguration
from .views import (
    HomeView, LoginView, LogoutView)

# try:
#     edc_app_configuration = EdcAppConfiguration()
#     edc_app_configuration.prepare()
# except OperationalError as e:
#     print('skipping edc configuration')
# except ProgrammingError as e:
#     print('skipping edc configuration')

urlpatterns = [
    url(r'^admin/logout/', LogoutView.as_view(url='/login/')),
    url(r'^login/', LoginView.as_view(), name='login_url'),
    url(r'^logout/', LogoutView.as_view(url='/login/'), name='logout_url'),
    url(r'^accounts/login/', LoginView.as_view()),
    url(r'^home/(?P<protocol_identifier>BHP[0-9]{3})/(?P<page>\d+)/', HomeView.as_view(), name='home'),
    url(r'^home/', HomeView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'', HomeView.as_view(), name='default'),
]

admin.site.site_header = 'DMIS Extract'
admin.site.site_title = 'DMIS Extract'
admin.site.index_title = 'DMIS Extract Admin'
# admin.site.site_url = '/admin/'
