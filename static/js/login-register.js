/*
 *
 * login-register modal
 * Autor: Creative Tim
 * Web-autor: creative.tim
 * Web script: http://creative-tim.com
 * 
 */
$(document).ready(function () {
    //Prepare csrf token
    var csrftoken = appMaster.getCookie('csrftoken');

    function showRegisterForm() {
        $('.loginBox').fadeOut('fast', function () {
            $('.registerBox').fadeIn('fast');
            $('.login-footer').fadeOut('fast', function () {
                $('.register-footer').fadeIn('fast');
            });
            $('.modal-title').html('Register with');
        });
        $('.error').removeClass('alert alert-danger').html('');

    }

    function showLoginForm() {
        $('#loginModal .registerBox').fadeOut('fast', function () {
            $('.loginBox').fadeIn('fast');
            $('.register-footer').fadeOut('fast', function () {
                $('.login-footer').fadeIn('fast');
            });

            $('.modal-title').html('Login with');
        });
        $('.error').removeClass('alert alert-danger').html('');
    }

    $("#btn_loginModal").click(function () {
        showLoginForm();
        setTimeout(function () {
            $('#loginModal').modal('show');
        }, 230);
    });


    $("#btn_registerModal").click(function () {
        showRegisterForm();
        setTimeout(function () {
            $('#loginModal').modal('show');
        }, 230);
    });

    $("#btn_login").click(function () {
        var login_email = $(".loginBox > form  > #login_email").val();
        var login_password = $(".loginBox > form > #login_password").val();
        var login_url = $(".loginBox > form").attr("action");

        $.ajax({
            type: "POST",
            url: login_url,
            data: {email: login_email, password: login_password, csrfmiddlewaretoken: csrftoken},
            success: function (data) {
                if (data.result == true) {
                    window.location.replace("/portfolio/" + data.url);
                } else {
                    shakeModal();
                }
            }
        });

        /*   Simulate error message from the server   */
        //shakeModal();
    });

    $("#login_password").keyup(function (e) {
        if (e.which == 13) { /* 13 == enter key@ascii */
            $("#btn_login").click();
        }
    });

    function shakeModal() {
        $('#loginModal .modal-dialog').addClass('shake');
        $('.error').addClass('alert alert-danger').html("Invalid email/password combination");
        $('input[type="password"]').val('');
        setTimeout(function () {
            $('#loginModal .modal-dialog').removeClass('shake');
        }, 1000);
    }

    if($("form >.errorlist").hasClass('errorlist')){
        openRegisterModal();
    }

    $("form > input[name*='commit']").click(function(){
        var email = $("#id_email").val();
        $("#id_username").val(email.split('@')[0]);
    });

    $(".inner-addon > input[name*='email']").keyup(function(){
        // 동일한 이메일이 있는지 검사
        $.ajax({
            type: "POST",
            url: $("#is_registered").val(),
            data: {email: this.value, csrfmiddlewaretoken: csrftoken},
            success: function (result) {
                var regExp = /^[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_\.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i;

                if (!regExp.test(result)) { // 이메일 validate 실패
                    reg_validate(".span_registerCheck.email", false, "5~20자의 영문 소문자, 숫자와 특수기호(_),(-)만 사용 가능합니다.");
                    $(".inner-addon > input[name*='email']").focus();
                    return false;
                }

                // 이메일 validate 성공
                reg_validate(".span_registerCheck.email", true, "");

            },
            error: function (result) {
                reg_validate(".span_registerCheck.email", false, "이미 사용중이거나 탈퇴한 아이디입니다.");
                $(".inner-addon > input[name*='email']").focus();
            }
        });
        return false;
    });

    $(".inner-addon > input[name*='password1']").keyup(function () {
        var regExp = /^[a-z0-9_]{4,20}$/;

        if(!regExp.test($(this).val())) {
            reg_validate(".span_registerCheck.password1", false, "6~16자 영문 대 소문자, 숫자, 특수문자를 사용하세요.");
            $(this).focus();
            return false;
        } else if($(this).val() == "") {
            reg_validate(".span_registerCheck.password1", false, "필수 정보입니다.");
            $(this).focus();
            return false;
        }

        reg_validate(".span_registerCheck.password1", true, "");
    });

    $(".inner-addon > input[name*='password2']").keyup(function () {
        var password1 = $(".inner-addon > input[name*='password1']").val();

        if (password1 != $(this).val()) {
            reg_validate(".span_registerCheck.password2", false, "비밀번호가 일치하지 않습니다.");
            return false;
        }  else if($(this).val() == "") {
            reg_validate(".span_registerCheck.password2", false, "필수 정보입니다.");
            return false;
        }

        reg_validate(".span_registerCheck.password2", true, "");
    });

    $("#frm_join").on('submit', function (e) {
        var btn_submit = $("#frm_join > input[name*=commit]");

        if (btn_submit.hasClass("disabled")) {
            return false;
        }
    });

    function reg_validate(ele, is_validate, msg){
        if (is_validate) {
            $(ele).html('<i class="xi-check-circle success"></i>');
            $(ele).attr({'chk':1});
            $('.error.registerBox').removeClass('alert alert-danger').html("");

            var chk = 0;

            $(".span_registerCheck").each(function () {
                if ($(this).attr("chk") == 1) {
                    chk++;
                }
            });

            if (chk == 3) {
                $("#frm_join > input[name*=commit]").removeClass("disabled");
            }
        } else {
            $(ele).html('<i class="xi-ban-circle fail"></i>');
            $(ele).attr({'chk':0});
            $('.error.registerBox').addClass('alert alert-danger').html(msg);
        }
    }
});
