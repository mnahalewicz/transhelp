import re

from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse

from django.shortcuts import render, redirect
from .models import RegistrationOffer

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def is_valid_token(token):
    offers = RegistrationOffer.objects.filter(token=token)
    if len(offers) == 0:
        return False
    if offers[0].was_executed:
        return False
    return True


def user_exists(username):
    if not is_valid_username(username):
        raise ValueError("bad username string")
    if len(User.objects.filter(username=username)) == 0:
        return False
    else:
        return True


def is_valid_username(username):
    return re.match("^[a-zA-Z0-9_\-]{3,}$", username) is not None


def is_valid_password(password):
    return re.match("^[a-zA-Z0-9_\-]{6,}$", password) is not None


def register(request):
    if "token" in request.GET:
        if is_valid_token(request.GET["token"]):
            request.session["registration_token"] = request.GET["token"]
        elif "registration_token" in request.session:
            del request.session["registration_token"]
    if "registration_token" in request.session and is_valid_token(request.session["registration_token"]):
        if "username" in request.POST and "password" in request.POST:
            token = request.session["registration_token"]
            username = request.POST["username"]
            password = request.POST["password"]
            if is_valid_username(username) and is_valid_password(password) and not user_exists(username):
                user = User.objects.create_user(username, password=password, email=None)
                user.save()
                offer = RegistrationOffer.objects.filter(token=token)[0]
                offer.was_executed = True
                offer.save()
                if not request.user.is_authenticated:
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)
                return redirect(reverse("list-rec"))
            else:
                return HttpResponseBadRequest()
        else:
            return render(request, 'registration/register.html')
    else:
        return HttpResponseForbidden()


def check_register_login(request):
    if "registration_token" in request.session and is_valid_token(request.session["registration_token"]):
        if "username" not in request.GET:
            return HttpResponseBadRequest()
        username = request.GET["username"]
        is_valid = is_valid_username(username)
        if not is_valid:
            response_dict = { "invalid" : True }
        elif user_exists(username):
            response_dict = { "exists" : True }
        else:
            response_dict = { "exists" : False }
        return JsonResponse(response_dict)
    else:
        return HttpResponseForbidden()











