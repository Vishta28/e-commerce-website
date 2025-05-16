from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_page, name='welcome_page'),
    path('active_buttons/', views.ActiveButtonsView.as_view(), name='active_buttons'),
    path('robots.txt', views.RobotstxtView.as_view()),
    path('product_feed', views.product_feed, name='product_feed'),
]

htmx_urlpatterns = [
    path('contact_info/', views.contact_info, name='contact_info'),
]

urlpatterns += htmx_urlpatterns
