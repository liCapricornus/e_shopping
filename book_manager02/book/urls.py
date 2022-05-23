from django.urls import path
from book.views import index

ulpatterns = [
    path('index/', index)
]