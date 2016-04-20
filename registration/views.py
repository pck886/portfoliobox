from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

def signup(request):

    if request.method == "POST":
        userform = UserCreationForm(request.POST)

        if userform.is_valid():
            userform.save()
            return HttpResponseRedirect(reverse("signup_ok"))

        return HttpResponseRedirect(reverse("home"))

    elif request.method == "GET":
        userform = UserCreationForm()

    return render(request, "login.html", {"userform" : userform})
