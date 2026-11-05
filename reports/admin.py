import json

from django.contrib import admin
from django.db.models.aggregates import Sum
from django.db.models.functions import ExtractMonth, ExtractWeek, ExtractYear
from reports import models
from django.utils.translation import gettext as _
from django.template.response import TemplateResponse

from store.models import Order
# Register your models here.
@admin.register(models.OrderReport)
class OrderReportAdmin(admin.ModelAdmin):
    change_list_template='admin/reports/order.html'

     
    def has_change_permission(self, request,obj=None):
            return False
    
    def has_add_permission(self, request,obj=None):
            return False

    def changelist_view(self, request, extra_context=None):
           yearly_state=(Order.objects.select_related('transaction')
                         .annotate(year=ExtractYear('created_at'))
                         .values('year').annotate(sum=Sum('transaction__amount')))
           monthly_state=(Order.objects.select_related('transaction')
                                    .annotate(year=ExtractYear('created_at'))
                                    .annotate(month=ExtractMonth('created_at'))
                                    .values('year','month').annotate(sym=Sum('transaction__amount')))
           weekly_state=(Order.objects.select_related('transaction')
                                    .annotate(year=ExtractYear('created_at'))
                                    .annotate(week=ExtractWeek('created_at'))
                                    .values('year','week').annotate(sym=Sum('transaction__amount')))

           
           
           context={
                  'yearly_state':json.dumps(list(yearly_state)),
                  'monthly_state':json.dumps(list(monthly_state)),
                  'weekly_state':json.dumps(list(weekly_state)),
                  **self.admin_site.each_context(request),
                  'title':_('Order')

           }
           return TemplateResponse(request,self.change_list_template,context)
