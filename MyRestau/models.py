from django.db import models
from django.contrib.auth.models import User



class Servante(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    date_time = models.DateTimeField(auto_now=True)

    def __str__(self) :
        return self.name

class Product(models.Model):
    name  = models.CharField(max_length=100)
    price =  models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField(default=0)
    barcode = models.CharField(max_length=40, unique=True)
    date_time = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name
    
class Facture(models.Model):
        servante = models.ForeignKey(Servante, on_delete=models.PROTECT)
        caissier = models.ForeignKey(User, on_delete=models.PROTECT)
        produits= models.ManyToManyField(Product, through='FactureProduit')
        date_time = models.DateTimeField(auto_now=True)

        def total(self):
          total = 0
          for factureproduit in self.factureproduit_set.all():
            total += factureproduit.product.price * factureproduit.quantiter
          return total

class FactureProduit(models.Model):
     facture = models.ForeignKey(Facture, on_delete=models.CASCADE)
     product = models.ForeignKey(Product, on_delete= models.CASCADE)
     quantiter = models.IntegerField(default=0)


