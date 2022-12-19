from django.urls import path
from . import views

urlpatterns = [ # IP 주소/
    path('', views.home),
    path('about_market/', views.about_market),
    path('my_page/', views.my_page),
]