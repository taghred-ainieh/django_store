from django.db import models
from django.utils.translation import gettext as _
# Create your models here.
class TransactionStatus(models.IntegerChoices):
    pending=0,_('Pending')
    Completed=1,_('Completed')

class PaymentMethod(models.IntegerChoices):
    Stripe=1,_('Stripe')
    paypal=2,_('Paypal')

class Transaction(models.Model):
    session=models.CharField(max_length=255)
    amount=models.FloatField()
    items=models.JSONField(default=dict)
    customer=models.JSONField(default=dict)
    status=models.IntegerField(choices=TransactionStatus.choices,default=TransactionStatus.pending)
    payment_method=models.IntegerField(

        choices=PaymentMethod.choices,
    )
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    @property
    def costomer_name(self):
        return f"{self.customer['first_name']} {self.customer['last_name']}"
    @property
    def costomer_email(self):
            return self.customer['email']
        
    
    
        
    
    