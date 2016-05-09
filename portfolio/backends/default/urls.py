
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView
from .views import PortfolioView

urlpatterns = [
    # url(r'^activate/complete/$',
    #     TemplateView.as_view(template_name='registration/activation_complete.html'),
    #     name='registration_activation_complete'),
    #
    #
    # url(r'^register/complete/$',
    #     TemplateView.as_view(template_name='registration/registration_complete.html'),
    #     name='registration_complete'),
    url(r'^closed/$',
        TemplateView.as_view(template_name='portfolio/portfolio_closed.html'),
        name='portfolio_disallowed'),
    # url(r'^/(?P<activation_key>\w+)/$',
    #     TemplateView.as_view(template_name='portfolio/portfolio.html'),
    #     name='registration_activate'),
]

if getattr(settings, 'INCLUDE_PORTFOLIO_URL', True):
    urlpatterns += [
        url(r'^(?P<portfolio_key>[-\w]+)/$',
            PortfolioView.as_view(),
            name='portfolio'),
    ]