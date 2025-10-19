from django.urls import path
from . import views

app_name = 'checkout'
urlpatterns = [
    path('init/<slug:slug>/', views.pay_init, name='pay_init'),
    path('verify/', views.pay_verify, name='pay_verify'),
]
