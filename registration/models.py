# -*- coding: utf-8 -*-

import datetime
import re
import random
import hashlib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.mail import EmailMultiAlternatives
from django.db import models, transaction
from django.shortcuts import render
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now as datetime_now
from django.utils import six

from .users import UserModel, UserModelString

SHA1_RE = re.compile('^[a-f0-9]{40}$')

class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    """
    def activate_user(self, activation_key, get_profile=False):
        """
        대응을 활성화 키를 확인하고 활성화
         ``User`` 경우 유효합니다.
         열쇠가 유효하고 만료되지 않은 경우,``User``를 반환
         활성화 후.
         키가 유효하지 않거나 만료 된 경우,``False``를 반환합니다.
         키가 유효하지만은``User``이 이미 활성화되어있는 경우,
         ``User``를 반환합니다.
         키는 유효하지만``User``가 비활성 상태, 반환``False``합니다.
         된 계정의 재 활성화를 방지하기 위해
         RegistrationProfile.activated````, 사이트 관리자에 의해 비활성화
         성공적으로 활성화 한 후 True````로 설정됩니다.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                # This is an actual activation failure as the activation
                # key does not exist. It is *not* the scenario where an
                # already activated User reuses an activation key.
                return False

            if profile.activated:
                # The User has already activated and is trying to activate
                # again. If the User is active, return the User. Else,
                # return False as the User has been deactivated by a site
                # administrator.
                if profile.user.is_active:
                    return profile.user
                else:
                    return False

            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                profile.activated = True

                with transaction.atomic():
                    user.save()
                    profile.save()

                if get_profile:
                    return profile
                else:
                    return user

        return False

    def create_inactive_user(self, site, new_user=None, send_email=True,
                             request=None, profile_info={}, **user_info):
        """
        새로운 비활성``User``를 생성하는 생성
         ``RegistrationProfile``과에 정품 인증 키를 이메일로
         ``User``, 반환 새로운``User``.
         기본적으로 활성화 이메일이 새로 전송됩니다
         사용자. 이을 사용하지 않으려면의 send_email = False````전달합니다.
         또한, 이메일이 전송되고`request``가 공급되면
         그것은 이메일 템플릿에 전달됩니다.
        """
        if new_user is None:
            password = user_info.pop('password')
            new_user = UserModel()(**user_info)
            new_user.set_password(password)
        new_user.is_active = False

        with transaction.atomic():
            new_user.save()
            registration_profile = self.create_profile(new_user, **profile_info)

        if send_email:
            registration_profile.send_activation_email(site, request)

        return new_user

    def create_profile(self, user, **profile_info):
        """
        Create a ``RegistrationProfile`` for a given
        ``User``, and return the ``RegistrationProfile``.
        The activation key for the ``RegistrationProfile`` will be a
        SHA1 hash, generated from a combination of the ``User``'s
        pk and a random salt.
        """
        profile =self.model(user=user, **profile_info)

        if 'activation_key' not  in profile_info:
            profile.create_new_activation_key(save=False)

        profile.save()

        return profile

    def resend_activation_mail(self, email, site, request=None):
        """
        Resets activation key for the user and resends activation email.
        """
        try:
            profile = self.get(user__email=email)
        except ObjectDoesNotExist:
            return False

        if profile.activated or profile.activation_key_expired():
            return False

        profile.create_new_activation_key()
        profile.send_activation_email(site, request)

        return True

    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated ``User``s.
        Accounts to be deleted are identified by searching for
        instances of ``RegistrationProfile`` with expired activation
        keys, and then checking to see if their associated ``User``
        instances have the field ``is_active`` set to ``False``; any
        ``User`` who is both inactive and has an expired activation
        key will be deleted.
        It is recommended that this method be executed regularly as
        part of your routine site maintenance; this application
        provides a custom management command which will call this
        method, accessible as ``manage.py cleanupregistration``.
        Regularly clearing out accounts which have never been
        activated serves two useful purposes:
        1. It alleviates the ocasional need to reset a
           ``RegistrationProfile`` and/or re-send an activation email
           when a user does not receive or does not act upon the
           initial activation email; since the account will be
           deleted, the user will be able to simply re-register and
           receive a new activation key.
        2. It prevents the possibility of a malicious user registering
           one or more accounts and never activating them (thus
           denying the use of those usernames to anyone else); since
           those accounts will be deleted, the usernames will become
           available for use again.
        If you have a troublesome ``User`` and wish to disable their
        account while keeping it in the database, simply delete the
        associated ``RegistrationProfile``; an inactive ``User`` which
        does not have an associated ``RegistrationProfile`` will not
        be deleted.
        """
        for profile in self.all():
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                        profile.delete()
            except UserModel().DoesNotExist:
                profile.delete()

@python_2_unicode_compatible
class RegistrationProfile(models.Model):
    """
    사용하기 위해 활성화 키를 저장하는 간단한 프로필
     사용자 계정 등록.
     일반적으로, 인스턴스와 직접 상호 작용하지 않습니다
     모델; 제공된 관리자는 방법을 포함한다
     청소뿐만 아니라, 새로운 계정을 생성 및 활성화
     활성화 된 적이없는 아웃 계정.
     그것이 가능하지만의 값으로,이 모델을 사용
     ``AUTH_PROFILE_MODULE`` 설정, 당신이하지 않는 것이 좋습니다
     그래서. 이 모델의 목적은 동안 데이터를 일시적으로 저장하는 것이다
     계정 등록 및 활성화.
    """
    user = models.OneToOneField(
        UserModelString(),
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    activation_key = models.CharField(_('activation key'), max_length=40)
    activated = models.BooleanField(default=False)

    objects = RegistrationManager()

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __str__(self):
        return "Registration information for %s" % self.user

    def create_new_activation_key(self, save=True):
        """
        Create a new activation key for the user
        """
        salt = hashlib.sha1(six.text_type(random.random())
                            .encode('ascii')).hexdigest()[:5]
        salt = salt.encode('ascii')
        user_pk = str(self.user.pk)

        if isinstance(user_pk, six.text_type):
            user_pk = user_pk.encode('utf-8')

        self.activation_key = hashlib.sha1(salt + user_pk).hexdigest()

        if save:
            self.save()

        return self.activation_key

    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired.
        Key expiration is determined by a two-step process:
        1. If the user has already activated, ``self.activated`` will
           be ``True``. Re-activating is not permitted, and so this
           method returns ``True`` in this case.
        2. Otherwise, the date the user signed up is incremented by
           the number of days specified in the setting
           ``ACCOUNT_ACTIVATION_DAYS`` (which should be the number of
           days after signup during which a user is allowed to
           activate their account); if the result is less than or
           equal to the current date, the key has expired and this
           method returns ``True``.
        """
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)

        return (self.activated or
                (self.user.date_joined + expiration_date <= datetime_now()))

    activation_key_expired.boolean = True

    def send_activation_email(self, site, request=None):
        """
        이과 관련된 사용자에게 활성화 이메일 보내기
        ``RegistrationProfile``.
        활성화 이메일은 다음 템플릿을 사용합니다,
        ACTIVATION_EMAIL_SUBJECT 설정하여 오버라이드 (override) 할 수있는,
        적절하게 ACTIVATION_EMAIL_BODY 및 ACTIVATION_EMAIL_HTML :
        ``등록 / activati​​on_email_subject.txt``
            이 템플릿의 제목란에 사용될
            이메일. 이 전자 메일의 제목 라인으로 사용되므로
            이 템플릿의 출력 ** 필수의 **이 될 만 한 줄
            본문; 한 줄 이상 출력은 강제적으로 가입됩니다
            단 하나의 라인으로.
        ``등록 / activati​​on_email.txt``
            이 템플릿은 이메일의 텍스트 본문에 사용된다.
        ``등록 / activati​​on_email.html``
            이 템플릿은 이메일의 HTML 바디를 위해 사용될 것이다.
        이러한 템플릿은 각각 다음과 같은 컨텍스트를 받게됩니다
        변수:
        ``user``
            새 사용자 계정
        ``activati​​on_key``
            새 계정의 활성화 키.
        ``expiration_days``
            남은 일 수있는 계정이 수도 중
            활성화 될 수있다.
        ``site``
            사이트를 나타내는 개체하는 사용자에
            등기; ``django.contrib.sites`` 여부에 따라
            설치되어,이 인스턴스가 될 수도 있고
            ``django.contrib.sites.models.Site`` (경우 사이트
            응용 프로그램이 설치된) 또는
            ``django.contrib.sites.requests.RequestSite`` (있는 경우
            아니). 장고 사이트에 대한 설명서를 참조하십시오
            이 객체의 인터페이스에 대한 자세한 내용은 프레임 워크입니다.
        ``request``
            옵션 장고의``HttpRequest`` 뷰에서 객체입니다.
            더 나은 템플릿에 전달됩니다 제공하는 경우
            RequestContext````을 통해 유연성을 제공합니다
        """
        activation_email_subject = getattr(settings, 'ACTIVATION_EMAIL_SUBJECT',
                                           'registration/email/activation_email_subject.txt')
        activation_email_body = getattr(settings, 'ACTIVATION_EMAIL_BODY',
                                        'registration/email/activation_email.txt')
        activation_email_html = getattr(settings, 'ACTIVATION_EMAIL_HTML',
                                        'registration/email/activation_email.html')

        ctx_dict = {}

        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)
        # RequestContext 후 업데이트 ctx_dict가 만들어집니다
        # 템플릿 상황에 맞는 프로세서 때문에
        # 사용자와 같은 값의 일부를 덮어 쓸 수 있습니다
        # django.contrib.auth.context_processors.auth를 사용
        ctx_dict.update({
            'user': self.user,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
        })
        subject = (getattr(settings, 'REGISTRATION_EMAIL_SUBJECT_PREFIX', '') +
                   render_to_string(
                       activation_email_subject, ctx_dict))
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        from_email = getattr(settings, 'REGISTRATION_DEFAULT_FROM_EMAIL',
                             settings.DEFAULT_FROM_EMAIL)
        message_txt = render_to_string(activation_email_body,
                                       ctx_dict)

        email_message = EmailMultiAlternatives(subject, message_txt,
                                               from_email, [self.user.email])

        if getattr(settings, 'REGISTRATION_EMAIL_HTML', True):
            try:
                message_html = render_to_string(
                    activation_email_html, ctx_dict)
            except TemplateDoesNotExist:
                pass
            else:
                email_message.attach_alternative(message_html, 'text/html')

        email_message.send()



def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except MultipleObjectsReturned as e:
        res = model.objects.filter(**kwargs).order_by("-id")
        return res[0]
    except Exception as e:
        return None
