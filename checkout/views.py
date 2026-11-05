import math
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.shortcuts import redirect, render,get_object_or_404
from django.template.loader import render_to_string
import stripe
from checkout.forms import UserInfoForm
from checkout.models import PaymentMethod, Transaction
from store.models import Cart, Order, Product,OrderProduct
from django.core.mail import send_mail
import requests
import json
import resend
from django.conf import settings

from django.http import HttpResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

# 1. الدالة المساعدة (تم تعديل التوجيه لإرجاع None لضمان سلامة البيانات)
def maketransection(request, pm):
    form = UserInfoForm(request.POST)
    if form.is_valid():
        cart = Cart.objects.filter(session=request.session.session_key).last()
        
        if not cart:
            return None  
            
        product = Product.objects.filter(pk__in=cart.items)
        total = 0
        for item in product:
            total += item.price
            
        if total <= 0:
            return None
            
        return Transaction.objects.create(
            customer=form.cleaned_data,
            session=request.session.session_key,
            payment_method=pm,
            items=cart.items, 
            amount=math.ceil(total),
        )
    else:
        return None # نرجع None هنا بدلاً من الـ redirect القديم لمنع أخطاء بايثون

# 2. الدالة الأساسية لاستقبال ضغطة زر الدفع (Stripe Checkout)
def strip_transaction(request):
    if request.method == 'POST':
        transaction = maketransection(request, PaymentMethod.Stripe)
        
        if transaction is None:
            return redirect('store_checkout')
            
        try:
            stripe_amount = int(transaction.amount * 100)
            host = request.build_absolute_uri('/')[:-1]
            
            success_link = host + "/checkout_complete?session_id={CHECKOUT_SESSION_ID}"
            cancel_link = host + "/checkout"
            
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"فاتورة طلب رقم #{transaction.id}",
                            },
                            'unit_amount': stripe_amount,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                 metadata={
                    'transaction': transaction.id
                },
                success_url=success_link,
                cancel_url=cancel_link,
            )
            
            # التحقق من وجود الرابط وإجبار بايثون على اعتباره نصاً (str) لحل تنبيه Pylance
            if checkout_session.url:
                return redirect(str(checkout_session.url), code=303)
            else:
                return HttpResponse("عذرًا، فشل إنشاء رابط الدفع من سيرفر Stripe.", status=400)
            
        except Exception as e:
            return HttpResponse(f"عذرًا، حدث خطأ أثناء تجهيز عملية الدفع: {str(e)}", status=500)
            
    return redirect('store_checkout')



    
            
        






