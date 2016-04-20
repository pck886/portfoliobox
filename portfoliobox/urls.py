"""portfoliobox URL Configuration

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
import common.views
import django.contrib.auth.views
import registration.views
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', common.views.home, name='home'),
    url(r'^introduce$', common.views.introduce, name='introduce'),
    # session
    url(r'^login/$', django.contrib.auth.views.login, name='login_url'),
    url(r'^logout/$', django.contrib.auth.views.logout, kwargs={'next_page': '/login/'}, name='logout_url'),
    url(r'^signup/$', registration.views.signup, name='signup'),
    url(r'^signup_ok/$', TemplateView.as_view(template_name='registration/templates/signup_ok.html'), name='signup_ok'),
    url(r'', include('social.apps.django_app.urls', namespace='social')),

]
