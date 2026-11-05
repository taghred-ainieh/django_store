from django.urls import path

from . import views
urlpatterns = [
    path('', views.index,name='store_home'),
    path('product/<int:id>', views.product,name='store_product'),
    path('category/<int:id>', views.category,name='store_category'),
    path('category', views.category,name='store_category'),
    path('cart', views.cart,name='store_cart'),
    path('cart/add/<int:id>',views.cart_add,name='cart_add'),
    path('cart/remove/<int:id>',views.cart_remove,name='cart_remove'),

    path('checkout_complete', views.checkout_complete,name='store_checkout_complete'),
    path('checkout', views.checkout,name='store_checkout'),
]