# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from ... import signals
from ...models import RegistrationProfile
from ...users import UserModel
from ...views import ActivationView as BaseActivationView
from ...views import RegistrationView as BaseRegistrationView


class RegistrationView(BaseRegistrationView):
    """
   간단한 워크 플로우를 따르는 등록 백엔드 :

    1. 사용자가 서명 비활성 계정이 만들어집니다.

    2. 이메일이 활성화 링크로 사용자에게 전송됩니다.

    3. 사용자 계정이 활성화되었습니다 활성화 링크를 클릭합니다.

    이 백엔드를 사용해야합니다

    *``은``INSTALLED_APPS`` 설정에 표시 registration``
      이 백엔드 수 있기 때문에 (일부 모델의 사용이 정의 신청).

    * 설정``ACCOUNT_ACTIVATION_DAYS``가 공급을 지정
      (정수로) 등록에서 일 수 동안
      사용자는 그 기간이 지나면 자신의 계정을 (활성화 할 수있는
      만료 활성화) 허용됩니다.

    * 템플릿의 생성
      ``등록 / activati​​on_email_subject.txt`` 및
      에 사용되는``등록 / activati​​on_email.txt``,
      활성화 이메일. 이 백엔드에 대한 정보를 참조하십시오
      이러한 템플릿에 대한 자세한 내용은``register`` 방법.

    이보기를 서브 클래 싱 할 때``SEND_ACTIVATION_EMAIL``을 설정할 수 있습니다
    False로 클래스 변수는 새 사용자에게 확인을 보내는 건너 뛰려면
    이메일 또는 설정`False````에`SEND_ACTIVATION_EMAIL``. 그래서 의미 하
    당신이 관리 사이트에서 수동으로 사용자를 활성화해야 할 것이다 또는
    다른 방법으로 활성화를 보냅니다. 예를 들어,에 의해 청취
    은``user_registered`` 신호.

    또한, 등록 일시를 추가하여 폐쇄 될 수있는
    ``REGISTRATION_OPEN``를 설정하고로 설정
    ``False``. ,이 설정을 생략하거나 True````로 설정
    등록이 현재 열려 있음을 의미하는 것으로 해석 및
    허용.

    내부적으로,이 활성 키에 저장을 통해 달성된다
    registration.models.RegistrationProfile````의 인스턴스. 만나다
    그 모델의 전체 설명서에 대한 사용자 지정 관리자의
    필드 및 지원 작업.

    """
    SEND_ACTIVATION_EMAIL = getattr(settings, 'SEND_ACTIVATION_EMAIL', True)
    success_url = 'registration_complete'

    def register(self, request):
        """
        사용자 이름, 이메일 주소와 비밀번호 감안할 때, 새로운 등록
         처음에는 비활성화됩니다 사용자 계정.

         새로운``User`` 객체와 함께, 새로운
         ``registration.models.RegistrationProfile``가 생성됩니다,
         정품 인증 키를 포함, 그``User``에 묶여있는
         이 계정에 사용됩니다.

         이메일이 제공된 이메일 주소로 발송됩니다; 이
         이메일은 활성화 링크가 포함되어야합니다. 이메일이 될 것입니다
         이 템플릿을 사용하여 렌더링합니다. 설명서를 참조하십시오
         ``RegistrationProfile.send_activation_email ()``에 대한
         제공 이러한 템플릿과 상황에 대한 정보
         그들.

         은``User``와``후 RegistrationProfile``가 만들어지고
         활성화 이메일이 신호를 전송
         ``registration.signals.user_registered``이 함께 전송됩니다
         키워드 인수``user``과 같은 새로운``User``
         보낸 사람으로이 백엔드의 클래스입니다.

        """
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password1 = request.POST.get("password1", "")

        site = get_current_site(self.request)

        # if hasattr(form, 'save'):
        #     new_user_instance = form.save()
        # else:
        #     new_user_instance = (UserModel().objects
        #                          .create_user(**form.cleaned_data))

        new_user_instance = (UserModel().objects.create_user(username=username, email=email, password=password1))

        new_user = RegistrationProfile.objects.create_inactive_user(
            new_user=new_user_instance,
            site=site,
            send_email=self.SEND_ACTIVATION_EMAIL,
            request=self.request,
        )
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def registration_allowed(self):
        """
        Indicate whether account registration is currently permitted,
        based on the value of the setting ``REGISTRATION_OPEN``. This
        is determined as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_success_url(self, user):
        return (self.success_url, (), {})


class ActivationView(BaseActivationView):
    def activate(self, *args, **kwargs):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activation_key = kwargs.get('activation_key', '')
        activated_user = (RegistrationProfile.objects
                          .activate_user(activation_key))
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=self.request)
        return activated_user

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})
