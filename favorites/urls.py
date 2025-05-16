from django.urls import path
from . import views

urlpatterns = [
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('favorites/add/', views.AddToFavoritesView.as_view(), name='add_to_favorites'),
    path('favorites/remove/', views.DeleteFromFavoritesView.as_view(), name='remove_from_favorites'),
]