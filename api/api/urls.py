from django.contrib import admin
from django.urls import path, include
from .views.views import TokenView, EventView
from .views.views_sumulas import SumulaView

app_name = 'api'


class ActiveSumulaView(SumulaView):
    def get(self, request):
        return self.get_active(request)

urlpatterns = [
    path('token/', TokenView.as_view(), name='token'),
    path('event/', EventView.as_view(), name='event'),
    path('sumula/', SumulaView.as_view(), name='sumula'),
    path('sumula/ativas/', ActiveSumulaView.as_view(), name='sumula-ativas'),
]
