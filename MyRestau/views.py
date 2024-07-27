from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib import messages
from django.views import View
from django.db import transaction

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate,login,logout

from xhtml2pdf import pisa
from datetime import datetime
from django.template.loader import get_template

from django.db.models import Q

from.models import *







class AddFactureView(View):
    template_name= 'addFacture.html'
    servantes = Servante.objects.all() 
    context = {
        'servantes':servantes
    }

    def get(self, request):
        return render(request,self.template_name, self.context)
    
    @transaction.atomic()
    def post(self, request):
        servante = request.POST.get('servante')

        facture_object = {
            'servante_id':servante,
            'caissier': request.user
        }

        facture = Facture.objects.create(**facture_object)
        if facture:
            facture.save()
        return redirect('idFacture', pk=facture.pk)         

def idFacture(request , pk):
    facture = Facture.objects.get(id=pk)

    context = {
        'facture':facture
    }
    if request.method=="POST":
        search_term = request.POST.get('barcode')
        quantiter= int(request.POST['quantiter'])
        try:
            produit = Product.objects.get(Q(barcode=search_term) | Q(name = search_term))



            if produit.stock >= quantiter:
                FactureProduit.objects.create(facture=facture, product=produit,quantiter=quantiter)
                #Mettre en jour le produit 
                produit.stock -= quantiter
                produit.save() 
                messages.success(request,("Produit ajouter !"))
            else:
                messages.error(request, "Stock insuffisant pour ce produit")
            return render (request,'idFacture.html',context)
        except Product.DoesNotExist:
            messages.error(request,'Produit non trouver')
    return render (request,'idFacture.html',context)


def stock(request):

    search_query = request.GET.get('search', '')
    if search_query:
        products = Product.objects.filter(nameicontains=search_query)  # Recherche par nom
    else:
        products = Product.objects.all()


    products = Product.objects.all().order_by('-date_time')

    paginator = Paginator(products, 10)  # Afficher 5 produits par page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products':products,
        'search': search_query, 
    }
    product = None
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        stock= request.POST['stock']
        barcode = request.POST['barcode']

        existing_product = Product.objects.filter(barcode=barcode)
        if existing_product.exists():
            messages.error(request, "Produit avec le même code barre existe déjà.")
        else :
          product = Product.objects.create(name=name , price=price , stock = stock, barcode =barcode)
        if product:
            product.save()
            messages.success(request,("Produit ajouter !"))
    return render (request,'stock.html',context)


def listFacture(request):
    if 'search_date' in request.GET:
        search_date = request.GET['search_date']
        factures = Facture.objects.filter(date_time__date=search_date).order_by('-date_time')
    else:
        factures = Facture.objects.all().order_by('-date_time')


    paginator = Paginator(factures, 5)  # Afficher 5 produits par page
    page = request.GET.get('page')
    try:
        factures = paginator.page(page)
    except PageNotAnInteger:
        factures = paginator.page(1)
    except EmptyPage:
       factures = paginator.page(paginator.num_pages)

    context = {
        'factures':factures,
       
    }
    return render (request, 'listFacture.html', context)


def delect_facture(request, pk):
        facture = Facture.objects.get(id=pk)
        if request.method =="POST":
            messages.warning(request,("Voulez-vous supprimer la facure !"))
            facture.delete()
            return redirect('listFactures')
        return render(request, 'delecte_facture.html') 

def delect_produit(request,pk):
    produit = Product.objects.get(id=pk)
    if request.method == "POST":
        messages.warning(request,("Vous avez supprimer le produit !"))
        produit.delete()
        return redirect('addProduct')
    return render (request, 'delect_produit.html')



def editProduit(request, pk):
    product = Product.objects.get(id=pk)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.barcode = request.POST['barcode']
        
        existing_product = Product.objects.exclude(id=pk).filter(barcode=product.barcode)
        if existing_product.exists():
            messages.error(request, "Un produit avec le même code barre existe déjà.")
        else:
            product.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect('stock')

    return render(request, 'editProduct.html', {'product': product})


def addStock(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == "POST":
        additionalstock = request.POST.get('additionalstock')
        product.stock += int(additionalstock)
        product.save()
        messages.success(request, f"Le stock pour le produit {product.name} a été mis à jour !")
        return redirect('stock')
    return render (request, 'addStock.html',{'product':product})



def generate_pdf(request,pk):
    obj = Facture.objects.get(id=pk)
    template = get_template('facturepdf.html')
    total = 0
    

    for factureproduit in obj.factureproduit_set.all():
       factureproduit.total = factureproduit.product.price * factureproduit.quantiter
       total += factureproduit.total
    
    # Generate the barcode image


  # Path to save the barcode image
   
      
    context = {
        'obj': obj,
        'print_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total': total,
        

    }
    html = template.render(context)

       # Adjust the width of the PDF to match the ticket size (57mm)
    css = '''
    <style>
    .ticket {
        font-family: Arial, sans-serif;
        width: 90mm;
        margin: 0 auto;
        padding: 10px;
    }
    
    h1 {
        text-align: center;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    th, td {
        border: 1px solid black;
        padding: 5px;
    }
    
    th {
        background-color: #f2f2f2;
    }
    
    tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    
    tr:nth-child(odd) {
        background-color: #ffffff;
    }
    
    td:last-child {
        text-align: right;
    }
    .barcode {
        text-align: center;
        margin-top: 20px;
        
        
    }

    </style>

    '''
    htmlwithcss = css + html 
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="output.pdf"'
    
    pisa.CreatePDF(htmlwithcss, dest=response)
    
    return response

def bila_journalier(request):

    today = datetime.now().date()
    factures = Facture.objects.filter(date_time__date = today).order_by('-date_time')
    total_general = 0

    for facture in factures:
        total_general += facture.total()

    context ={
        'today':today,
        'factures':factures,
        'total_general':total_general
    } 

    return render(request,'bilan_journalier.html', context)  


def caissier_bilan(request):
     connected_caisser = request.user
     today = datetime.now().date()
     factures = Facture.objects.filter(caissier = connected_caisser , date_time__date = today).order_by('-date_time')

     total_general = 0

     for facture in factures:
        total_general += facture.total()
    
     context = {
         
         'today':today,
         'factures': factures,
         'total_general': total_general

     }
     return render(request, 'caissier_bilan.html', context)

def register_servante(request):
    if request.method =='POST':
        name = request.POST['name']
        phone = request.POST['phone']
        servante = Servante.objects.create(name=name, phone=phone)
        if servante:
            servante.save()
            messages.success(request,'servant(e) creer avec succes')
    return render(request, 'register_servante.html')



def listServante(request):
    servantes = Servante.objects.all()
    context ={
        'servantes':servantes
    }
    return render (request, 'listServante.html',context)

def supprimer_servante(request,pk):
    servante = Servante.objects.get(id=pk)
    servante.delete()
    return redirect ('listServante')


def listCaissier(request):
    users = User.objects.filter(is_superuser = False)
    context ={
        'users':users
    }
    return render (request,'listCaissier.html', context)

def supprimer_caissier(request, pk):
    caissier =  User.objects.get(id=pk)
    caissier.delete()
    return redirect('lisCaissier')

def register(request):
    if request.method=='POST':
        username=request.POST['name']
        password=request.POST['password']
        mon_utilisateur=User.objects.create_user(username=username,password=password)
        mon_utilisateur.frist_name=username
        mon_utilisateur.save()
        messages.success(request,'compte creer avec succes')
    return render(request, 'compte/register_caissier.html')


def acces(request):
    if request.method=="POST":
        username=request.POST['name']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            if user.is_superuser:
              return redirect('stock')
            else:
                return redirect('addFacture')
        else:
            messages.error(request,'Utilisateur et Mot de passe non trouver')       
    return render(request,'compte/access.html')

def logoutuser(request):
    logout(request)
    return redirect('/')
