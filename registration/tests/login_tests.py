# -*- coding: utf-8 -*-

import json

from django.apps import apps
from django.core.urlresolvers import reverse
from django.test import TestCase
from registration.models import RegistrationProfile
from registration.users import UserModel

Site = apps.get_model('sites', 'Site')

class DefaultLoginViewests(TestCase):
    """
    로그인 테스트
    """

    def setUp(self):
        self.user_info = {
            'username': 'bob',
            'password': 'secret',
            'email': 'bob@example.com'
        }

        new_user = UserModel().objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        RegistrationProfile.objects.activate_user(profile.activation_key)

    def tearDown(self):
      return

    def test_loginview_success(self):
        """
        정상적인 르고인 테스트
        """
        resp = self.client.post(
            reverse('auth_login'),
            data={'email': 'bob@example.com',
                  'password': 'secret'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(True, result_data['result'])

    def test_loginview_blank(self):
        """
        로그인 이메일과 패스워드가 없는 경우
        """
        resp = self.client.get(
            reverse('auth_login'),
            data={'email': '',
                  'password': ''}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(False, result_data['result'])

    def test_loginview_blank_email(self):
        """
        로그인 이메일이 없는 경우
        """
        resp = self.client.post(
            reverse('auth_login'),
            data={'email': '',
                  'password': 'secret'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(False, result_data['result'])

    def test_loginview_blank_password(self):
        """
        로그인 패스워드가 없는 경우
        """
        resp = self.client.post(
            reverse('auth_login'),
            data={'email': 'bob@example.com',
                  'password': ''}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(False, result_data['result'])

    def test_loginview_wrong_password(self):
        """
        로그인 패스워드가 틀린 경우
        """
        resp = self.client.post(
            reverse('auth_login'),
            data={'email': 'bob@example.com',
                  'password': 'qwer1234'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(False, result_data['result'])

    def test_loginview_form_method_get(self):
        """
        로그인 FORM METHOD를 GET으로 전송한 경우
        """
        resp = self.client.get(
            reverse('auth_login'),
            data={'email': 'bob@example.com',
                  'password': 'secret'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        result_data = json.loads(resp.content)

        self.assertEqual(False, result_data['result'])

