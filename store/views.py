from django.core import paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from store.models import Cart, Category, Product, Slider
from django.contrib import messages as django_messages 
# Create your views here.
def index(request):
    model=Product.objects.select_related('author').filter(featured=True)
    sileds=Slider.objects.order_by('order')
    return render(request,'index.html',{'products':model,'slides':sileds})



def cart(request):
    return render(request,'cart.html')



def category(request, id=None):
    # 1. التقاط القيم القادمة من المتصفح
    query = request.GET.get('query')
    final_id = id or request.GET.get('Category')
    cat=None
    where={}
    # 3. الفلترة بالتصنيف (إذا كانت القيمة رقماً فعلياً فقط)
    if final_id and str(final_id).isdigit():
        cat=Category.objects.get(pk=final_id)
        where['category_id']=final_id
    
    # 4. الفلترة بنص البحث (إذا كتب المستخدم اسماً)
    if query:
        where['name__icontains'] = query
    models=Product.objects.filter(**where)
    # 5. الترقيم وعرض الصفحة
    paginator = Paginator(models, 2)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'category.html', {'page_obj': page_obj,'cat':cat})



def checkout_complete(request):
    Cart.objects.filter(session=request.session.session_key).delete()

    return render(request,'checkout-complete.html')


def checkout(request):
    return render(request,'checkout.html')


def product(request,id):
    model=Product.objects.get(pk=id)
    return render(request,'product.html',{'product':model})




def cart_add(request,id):
    if not request.session.session_key:
        request.session.create()
    session_id=request.session.session_key
    cart_model=Cart.objects.filter(session=request.session.session_key).last()
    if cart_model is None:
        cart_model=Cart.objects.create(session_id=session_id,items=[id])
    elif id not in cart_model.items:
        cart_model.items.append(id)
        cart_model.save()

    django_messages.success(request, _('the product has been added to your cart'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def cart_remove(request,id):
    session=request.session.session_key
    if not session:
        return JsonResponse({})
    cart_model=Cart.objects.filter(session=request.session.session_key).last()
    if not cart_model:
        return JsonResponse({})
    cart_model.items.remove(id)
    cart_model.save()
    django_messages.success(request, _('the product has been removed from your cart'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))