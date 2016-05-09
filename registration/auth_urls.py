"""
URL patterns for the views included in ``django.contrib.auth``.
Including these URLs (via the ``include()`` directive) will set up the
following patterns based at whatever URL prefix they are included
under:
* User login at ``login/``.
* User logout at ``logout/``.
* The two-step password change at ``password/change/`` and
  ``password/change/done/``.
* The four-step password reset at ``password/reset/``,
  ``password/reset/confirm/``, ``password/reset/complete/`` and
  ``password/reset/done/``.
The default registration backend already has an ``include()`` for
these URLs, so under the default setup it is not necessary to manually
include these views. Other backends may or may not include them;
consult a specific backend's documentation for details.
"""
import registration
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$',
        registration.views.login_view,
        name='auth_login'),
    url(r'^logout/$',
        auth_views.logout,
        {'template_name': 'index.html'},
        name='auth_logout'),
]