from django.db import models



class ProductMaster(models.Model):
    name = models.CharField(max_length=100)
    stock=models.IntegerField(default=0)
    purchase_price = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3) #original price of teh product
    tax_percentage =models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3) #tax for the single item
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table='product_master'
        ordering = ('created_at',)


class PurchaseHistory(models.Model):
    customer_email = models.EmailField(max_length=100, blank=True, null=True)
    total_without_tax = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    total_tax = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    net_total = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    rounded_total =models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    amount_paid = models.DecimalField(max_digits=10,decimal_places=3,null=True,blank=True)
    change_given = models.JSONField(blank=True, null=True)
    balance =models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table='purchase_history'
        ordering = ('created_at',)


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(PurchaseHistory, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3) #selling price
    tax_amount = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    total_price = models.DecimalField(max_digits=10,blank=True,null=True,decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table='purchase_item'
        ordering = ('created_at',)



class Denomination(models.Model):
    value = models.IntegerField(blank=True, null=True)
    available_count =models.IntegerField(blank=True,null=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table='denomination'
        ordering = ('created_at',)