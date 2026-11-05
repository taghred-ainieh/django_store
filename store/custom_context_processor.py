from store.models import Category,Cart,Product


def store_website(request):
    categories=Category.objects.order_by('order')
    cart=Cart.objects.filter(session=request.session.session_key).last()
    cart_total=0
    cart_product=[]
    if cart:
        cart_product=Product.objects.filter(pk__in=cart.items)
        for item in cart_product:
            cart_total=cart_total+item.price

    return{'categories':categories,
           'cart_product':cart_product,
           'cart_total':cart_total,}

