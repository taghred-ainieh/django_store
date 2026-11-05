from django.urls import path
from . import views
from . import webhook
urlpatterns = [
    # path('order',views.makeorder,name='checkout_order')

    
    
    path('checkout/stripe/', views.strip_transaction, name='create-stripe-session'),
    path('stripe/webhook/',webhook.stripe_webhook,name='strip_webhok'),

]