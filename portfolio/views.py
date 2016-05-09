# -*- coding: utf-8 -*-
from django.shortcuts import redirect, render_to_response, render

from django.views.generic import TemplateView


class PortfolioView(TemplateView):
    """
    Base class for user activation views.
    """
    disallowed_url = 'portfolio_disallowed'
    http_method_names = ['get']


    def get(self, request, *args, **kwargs):

        """
        Portfolio 사용여부와 권한 체크하는 부분
        """
        is_user = self.is_user(*args, **kwargs)

        if not self.portfolio_allowed():
            return redirect(self.disallowed_url)

        if is_user:
            success_url = self.get_success_url(*args, **kwargs)

            # success_url may be a simple string, or a tuple providing the
            # full argument set for redirect(). Attempting to unpack it
            # tells us which one it is.
            try:
                to, args, kwargs = success_url
            except ValueError:
                return redirect(self.disallowed_url)
            else:
                return render(request, to)

        elif not is_user:
            return redirect(self.disallowed_url)

        return super(PortfolioView, self).get(request, *args, **kwargs)

    def portfolio_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.
        """
        return True

    def is_user(self, *args, **kwargs):

        raise NotImplementedError

    def get_success_url(self, user):
        """
        Use the new user when constructing success_url.

        """

        # url = ''
        #
        # if super(PortfolioView, self).get_success_url() is None:
        #     url = self.template_name
        # else:
        #     url = super(PortfolioView, self).get_success_url()

        raise NotImplementedError
