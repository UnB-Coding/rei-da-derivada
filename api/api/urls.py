from django.contrib import admin
from django.urls import path, include
from .views import TokenView, EventView

app_name = 'api'

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
]
