from django.conf import settings
from django.contrib.admin import helpers
from django.core import mail, urlresolvers
from django.test import TestCase
from django.test.client import Client
from registration.models import RegistrationProfile
from registration.users import UserModel

class AdminCustomActionsTestCase(TestCase):
    """
    Test the available admin custom actions
    """

    def setUp(self):
        self.client = Client()
        admin_user = UserModel().objects.create_superuser('admin', 'admin@test.com', 'admin')
        self.client.login(username=admin_user.username, password=admin_user)

        self.user_info = {
            'username': 'alice',
            'password': 'swordfish',
            'email': 'alice@example.com'
        }

        self.old_activation = getattr(settings,
                                      'ACCOUNT_ACTIVATION_DAYS', None)
        self.old_reg_email = getattr(settings,
                                     'REGISTRATION_DEFAULT_FROM_EMAIL', None)
        self.old_email_html = getattr(settings,
                                      'REGISTRATION_EMAIL_HTML', None)
        self.old_django_email = getattr(settings,
                                        'DEFAULT_FROM_EMAIL', None)
        self.old_auth_user = getattr(settings,
                                     'AUTH_USER_MODEL', None)

        settings.ACCOUNT_ACTIVATION_DAYS = 7
        settings.REGISTRATION_DEFAULT_FROM_EMAIL = 'registration@email.com'
        settings.REGISTRATION_EMAIL_HTML = True
        settings.DEFAULT_FROM_EMAIL = 'django@email.com'
        settings.AUTH_USER_MODEL = 'auth.User'

    def tearDown(self):
        settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation
        settings.REGISTRATION_DEFAULT_FROM_EMAIL = self.old_reg_email
        settings.REGISTRATION_EMAIL_HTML = self.old_email_html
        settings.DEFAULT_FROM_EMAIL = self.old_django_email
        settings.AUTH_USER_MODEL = self.old_auth_user

    def test_activate_users(self):
        """
        Test the admin custom command 'activate users'

        """
        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        self.assertFalse(profile.activated)

        registrationprofile_list = urlresolvers.reverse('admin:registration_registrationprofile_changelist')
        post_data = {
            'action': 'activate_users',
            helpers.ACTION_CHECKBOX_NAME: [profile.pk]
        }
        self.client.post(registrationprofile_list, post_data, follow=True)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertTrue(profile.activated)


    #C:\python_project\portfoliobox\venv\lib\site-packages\django\template\loader.py:97: RemovedInDjango110Warning: render() must be called with a dict, not a RequestContext.
    #return template.render(context, request)

    # def test_resend_activation_email(self):
    #     """
    #     Test the admin custom command 'resend activation email'
    #     """
    #     new_user = UserModel().objects.create_user(**self.user_info)
    #     profile = RegistrationProfile.objects.create_profile(new_user)
    #
    #     registrationprofile_list = urlresolvers.reverse('admin:registration_registrationprofile_changelist')
    #     post_data = {
    #         'action': 'resend_activation_email',
    #         helpers.ACTION_CHECKBOX_NAME: [profile.pk]
    #     }
    #     self.client.post(registrationprofile_list, post_data, follow=True)
    #
    #     self.assertEqual(len(mail.outbox), 1)
    #     self.assertEqual(mail.outbox[0].to, [self.user_info['email']])