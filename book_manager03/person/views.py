from django.shortcuts import render

# Create your views here.

def index(request):
    return HttpResponse('给文明以岁月，给时代以AI.')