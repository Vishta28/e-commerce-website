from django.urls import path
from . import views

urlpatterns = [
    path('comparison/', views.ComparisonView.as_view(), name='comparison'),
    path('comparison/add', views.AddToComparisonView.as_view(), name='add_to_comparison'),
    path('comparison/remove', views.DeleteFromComparisonView.as_view(), name='remove_from_comparison'),
]