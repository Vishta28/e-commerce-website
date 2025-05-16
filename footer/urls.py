from django.urls import path
from . import views

urlpatterns = [
    path('policy/', views.policy, name='policy'),
]