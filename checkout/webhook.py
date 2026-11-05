
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe

from store.models import Order,Product,OrderProduct
from django.core.mail import send_mail
from django.template.loader import render_to_string
import resend
from . import models
from django.http import HttpResponse, JsonResponse

import os
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"❌ خطأ في التحقق من التوقيع الرقمي لـ Stripe: {str(e)}")
        return HttpResponse(status=400)

    # استقبال حدث إتمام الدفع بنجاح
    if event.type == 'checkout.session.completed':
        session = event.data.object
        transaction_id = session.metadata['transaction']

        
        print(f" Let's Go: تم استقبال حدث النجاح للـ Transaction رقم: {transaction_id}")
         
        if transaction_id:
            # تشغيل الدالة وفحص هل تمت بنجاح أم فشلت
            success = makeorder(transaction_id)
            if not success:
                print("❌ فشلت دالة makeorder في إتمام الحفظ")
            else:
                print("✅ تم حفظ Order و OrderProduct بنجاح وإرسال الإيميل")
            
    return JsonResponse({'success': True})


import json

def makeorder(tran_id):
    try:
        # 1. جلب الفاتورة وتحديث حالتها إلى مكتملة
        transaction = models.Transaction.objects.get(pk=tran_id)
        transaction.status = 1  # Completed
        transaction.save()
        
        # 2. إنشاء الطلب الأساسي
        order = Order.objects.create(transaction=transaction)
        print(f"✔️ تم تدوين الطلب رقم {order.id} بنجاح في قاعدة البيانات.")
        
        # 3. معالجة الـ items وفك تشفيرها بشكل آمن مهما كان نوعها القادم
        raw_items = transaction.items
        product_ids = []
        
        if isinstance(raw_items, str):
            try:
                raw_items = json.loads(raw_items)
            except Exception:
                pass
                
        if isinstance(raw_items, dict):
            product_ids = list(raw_items.keys())
        elif isinstance(raw_items, list):
            product_ids = raw_items
        else:
            product_ids = [raw_items] if raw_items else []

        # 4. جلب المنتجات وبناء سجلات المشتريات
        products = Product.objects.filter(pk__in=product_ids)
        
        for product in products:
            OrderProduct.objects.create(
                order=order,
                product=product,
                price=product.price
            )
            print(f"✔️ تم ربط المنتج {product.name} بالطلب.")
            
        # 5. إرسال الإيميل
        msg_html = render_to_string('emails/order.html', {'order': order, 'product': products})
        recipient_email = str(transaction.customer.get('email', ''))
        
        if recipient_email:
            params: resend.Emails.SendParams = {
                "from": "onboarding@resend.dev",
                "to": [recipient_email],
                "subject": "Order Complete",
                "html": msg_html,
            }
            resend.Emails.send(params)
            
        return True

    except models.Transaction.DoesNotExist:
        print(f"❌ خطأ قاتل: الفاتورة رقم {tran_id} غير موجودة أساساً في قاعدة البيانات!")
        return False
    except Exception as e:
        print(f"❌ انهار الكود تماماً داخل makeorder بسبب الخطأ التالي: {str(e)}")
        return False
