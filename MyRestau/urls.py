

from django.urls import path
from.import views



urlpatterns = [
    path('',views.acces, name='acces'),
    path('addFacture', views.AddFactureView.as_view(), name='addFacture'),
    path('idFacture/<str:pk>', views.idFacture, name="idFacture"),
    path('estock/', views.stock, name='stock'),
    path('listFacture/', views.listFacture, name='listFactures'),
    path('delectFacture/<str:pk>',views.delect_facture, name='delectFacture'),
    path('delect_produit/<str:pk>', views.delect_produit, name='delect_produit'),
    path('editProduit/<str:pk>', views.editProduit, name='editProduit'),
    path('addStock/<str:pk>', views.addStock, name='addStock'),
    path('generatepdf/<int:pk>', views.generate_pdf, name='generate_pdf'),
    path('bilanJournalier/', views.bila_journalier, name= 'bilan_journalier'),
    path('caissier_bilan/', views.caissier_bilan, name='caissier_bilan'),
    path('register/', views.register, name='register'),
    path('register_servante/', views.register_servante, name='register_servante'),
    path('listServante/',views.listServante, name='listServante'),
    path('listCaissier/', views.listCaissier, name='lisCaissier'),
    path('delectCaissier/<str:pk>', views.supprimer_caissier, name='delect_caissier'),
    path('delect_sevante/<str:pk>', views.supprimer_servante, name='delect_servante'),
    path('logout/', views.logoutuser, name='logoutUser')
  
]
