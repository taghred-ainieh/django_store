from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from  . import models

# Register your models here.
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page=20



@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_per_page=20


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_per_page=20


@admin.register(models.Slider)
class SliderAdmin(admin.ModelAdmin):
    list_per_page=20


@admin.register(models.Order)
class OrderrAdmin(admin.ModelAdmin):
    list_per_page=20
    list_select_related=['transaction']
    list_display=['id','amount','items','email','method']
    def amount(self,obj):
        if obj.transaction:
            return obj.transaction.amount
        return '-'
    def items (self,obj):
          if obj.transaction and obj.transaction.items:
                    return len(obj.transaction.items)
          return '-'
    def email (self,obj):
              if obj.transaction:
                        return  obj.transaction.customer.get('email')
              return '-'
    def method (self,obj):
                  if obj.transaction:
                            return  obj.transaction.get_payment_method_display()
                  return '-'
    
        

    
    def has_change_permission(self, request,obj=None):
        return False

    def has_add_permission(self, request,obj=None):
        return False
    