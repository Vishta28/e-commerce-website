from django.urls import path
from . import views

urlpatterns = [
    path('store/models/<str:category>/', views.ModelView.as_view(), name='models_page'),
    path('store/models/constructor/<str:category>/<str:model>/', views.ItemListPage.as_view(), name='constructor_page'),
    path('store/models/menu', views.ModelsCategoryMenu.as_view(), name='models_menu'),
]

htmx_urlpatterns = [
    path('store/<str:category>/', views.ItemsModel.as_view(), name='models_list'),
    path('dynamic_shop/product/<str:category>/<str:model>', views.ModelsConstructorView.as_view(), name='constructor_results'),
    # path('dynamic_shop/<str:category>/<str:model>/<slug:slug>/', views.DynamicShopProduct.as_view(), name='dynamic_shop'),
    path('models_constructor/options/', views.ConstructorOptionsView.as_view(), name='constructor_options'),
    path('models_info/<str:model>/<str:category>/', views.ModelItemsInfo.as_view(), name='models_info'),
    path('quick_model_view/<str:category>/<str:model>/', views.QuickModelView.as_view(), name='quick_model_view'),
    path('favorite_products', views.FavoriteProductsView.as_view(), name='favorite_products')

]

urlpatterns += htmx_urlpatterns