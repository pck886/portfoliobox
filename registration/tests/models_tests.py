import datetime
import hashlib
import re

from django.utils import six
from django.apps import apps
from django.conf import settings
from django.core import mail
from django.core import management
from django.test import TestCase

from registration.models import RegistrationProfile
from registration.users import UserModel

Site = apps.get_model('sites', 'Site')


class RegistrationModelTests(TestCase):
    """
    Test the model and manager used in the default backend.

    """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def setUp(self):
        self.old_activation = getattr(settings,
                                      'ACCOUNT_ACTIVATION_DAYS', None)
        self.old_reg_email = getattr(settings,
                                     'REGISTRATION_DEFAULT_FROM_EMAIL', None)
        self.old_email_html = getattr(settings,
                                      'REGISTRATION_EMAIL_HTML', None)
        self.old_django_email = getattr(settings,
                                        'DEFAULT_FROM_EMAIL', None)

        settings.ACCOUNT_ACTIVATION_DAYS = 7
        settings.REGISTRATION_DEFAULT_FROM_EMAIL = 'registration@email.com'
        settings.REGISTRATION_EMAIL_HTML = True
        settings.DEFAULT_FROM_EMAIL = 'django@email.com'
    def tearDown(self):
        settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation
        settings.REGISTRATION_DEFAULT_FROM_EMAIL = self.old_reg_email
        settings.REGISTRATION_EMAIL_HTML = self.old_email_html
        settings.DEFAULT_FROM_EMAIL = self.old_django_email

    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA1 hash to use as
        activation key.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.failUnless(re.match('^[a-f0-9]{40}$', profile.activation_key))
        self.assertEqual(six.text_type(profile),
                         "Registration information for alice")

    def test_activation_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_activation_email_user_registration_default_from_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(mail.outbox[0].from_email, 'registration@email.com')

    def test_activation_email_falls_back_to_django_default_from_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        settings.REGISTRATION_DEFAULT_FROM_EMAIL = None
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(mail.outbox[0].from_email, 'django@email.com')

    def test_activation_email_is_plain_text_if_html_disabled(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an html
        email by default.

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox[0].alternatives), 1)

    def test_activation_email_is_plain_text_if_html_disabled(self):
        """
        ``RegistrationProfile.send_activation_email`` sends a plain
        text email if settings.REGISTRATION_EMAIL_HTML is False.

        """
        settings.REGISTRATION_EMAIL_HTML = False
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())

        self.assertEqual(len(mail.outbox[0].alternatives), 0)

    def test_user_creation(self):
        """
        Creating a new user populates the correct data, and sets the
        user's account inactive.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)

        self.assertEqual(new_user.username, 'alice')
        self.assertEqual(new_user.email, 'alice@example.com')
        self.failUnless(new_user.check_password('swordfish'))
        self.failIf(new_user.is_active)

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(), **self.user_info)

        self.assertEqual(len(mail.outbox), 1)