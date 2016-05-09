# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from portfolio.views import PortfolioView as BasePortfolioView
from registration.models import get_or_none

template_name = 'portfolio/portfolio.html'

class PortfolioView(BasePortfolioView):

    def is_user(self, *args, **kwargs):

        """
        권한 체크하는 부분
         추후 URL 체크(뒤에 user_id가 붙어 오는지 아닌지) 로직 추가
        """
        porfolio_key = kwargs.get('portfolio_key', '')

        username = get_or_none(User, username=porfolio_key)

        if not username:
            return False

        return True

    def portfolio_allowed(self):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'PORTFOLIO_OPEN', True)

    def get_success_url(self, *args, **kwargs):
        portfolio_key = kwargs.get('portfolio_key', '')

        return (template_name, (), {'portfolio_key': portfolio_key})