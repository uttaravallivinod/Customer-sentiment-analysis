
from django.urls import path,include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.login),
    path('signup',views.signup),
    path('dashboard',views.dashboard),
    path('senti/<pk>',views.senti),
    path('feedhome',views.fhome),
    path('feed/<pk>',views.text_feedback),
    path('products/<pk>',views.products),
    path('addorg',views.addorg),
    path('addproduct/<pk>',views.addproduct),
    path('video/<pk>',views.video),
    path('audio/<pk>',views.audio),
    path('smedia/<pk>',views.smedia),
]
