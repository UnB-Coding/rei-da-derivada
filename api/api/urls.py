from django.urls import re_path, path
from . import views

app_name = 'api'

urlpatterns = [
    path('token/', views.Token.as_view(), name='token'),

]

