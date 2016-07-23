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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^$', common.views.home, name='home'),
#     url(r'^introduce$', common.views.introduce, name='introduce'),
#     # session
#     url(r'^login/$', django.contrib.auth.views.login, name='login_url'),
#     url(r'^logout/$', django.contrib.auth.views.logout, kwargs={'next_page': '/login/'}, name='logout_url'),
#     url(r'^signup/$', registration.views.RegistrationView.register, name='register'),

#     url(r'', include('social.apps.django_app.urls', namespace='social')),
#
# ]

urlpatterns = [
    url(r'^$',
        TemplateView.as_view(template_name='index.html'),
        name='index'),

    url(r'^accounts/',
        include('registration.backends.default.urls')),

    url(r'^portfolio/',
        include('portfolio.backends.default.urls')),

    url(r'^accounts/profile/',
        TemplateView.as_view(template_name='profile.html'),
        name='profile'),

    url(r'^admin/',
        include(admin.site.urls),
        name='admin'),

    url(r'^edu/',
        TemplateView.as_view(template_name='edupot/edupot.html'),
        name='edu'),

    url(r'^yaja/',
        TemplateView.as_view(template_name='yaja/index.html'),
        name='yaja'),
]