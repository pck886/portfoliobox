# -*- coding: utf-8 -*-
"""
Views which allow users to create and activate accounts.
"""
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView

from registration.models import get_or_none

class RegistrationView(TemplateView):
    """
    Base class for user registration views.
    """
    disallowed_url = 'registration_disallowed'
    http_method_names = ['post', 'head', 'options', 'trace']
    template_name = 'index.html'

    @method_decorator(sensitive_post_parameters('password1', 'password2'))
    def dispatch(self, request, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.
        view 보기의 일부 - 받아들이는 방법 request 인수 플러스 인수를하고,
        HTTP 응답을 반환합니다.
        """

        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))

        if not self.registration_allowed() or (user is not None):
            return redirect(self.disallowed_url)

        new_user = self.register(request)

        if new_user:
            success_url = self.get_success_url(new_user)

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
        except ValueError:
            return redirect(success_url)
        else:
            return redirect(to, *args, **kwargs)

        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return True

    def register(self, request):
        """
        Implement user-registration logic here.
        """

        raise NotImplementedError

    def get_success_url(self, user=None):
        """
        Use the new user when constructing success_url.

        """
        return super(RegistrationView, self).get_success_url()

class ActivationView(TemplateView):
    """
    Base class for user activation views.
    """
    http_method_names = ['get']
    template_name = 'registration/activate.html'

    def get(self, request, *args, **kwargs):
        activated_user = self.activate(*args, **kwargs)

        if activated_user:
            success_url = self.get_success_url(activated_user)

            try:
                to, args, kwargs = success_url
            except ValueError:
                return redirect(success_url)
            else:
                return redirect(to, *args, **kwargs)

        return super(ActivationView, self).get(request, *args, **kwargs)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.
        """
        raise NotImplementedError

    def get_success_url(self, user):
        raise NotImplementedError


def is_registered(request):
    if (request.method == "POST"):
        email = request.POST.get("email", "")

        if get_or_none(User, email=email) is None:
            return HttpResponse(email, status=200)

    return HttpResponse(email, status=400)

def login_view(request):
    if (request.method == 'POST'):
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active and user.registrationprofile.activated:
                login(request, user)
                request.session.set_expiry(31536000)
                user.last_login
                return JsonResponse({'result': True, 'url': user.username})

    return JsonResponse({'result': False})

