from django.http import HttpResponse
from django.shortcuts import render, redirect
import requests
import re
from django.conf import settings
from django.conf.urls.static import static


def index(request):
  return render(request, 'index.html')

def post(request):
  if request.method == 'POST':
    print(request.POST)
  return HttpResponse("HI")