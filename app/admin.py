from django.contrib import admin
from .models import Profile, purchaseOrder, saleOrder

admin.site.register([Profile, purchaseOrder, saleOrder])
