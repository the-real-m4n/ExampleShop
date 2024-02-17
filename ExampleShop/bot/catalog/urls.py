from django.urls import path
from .views import Product,ProductForm
urlpatterns=[
    path('',Product ,name='product'),
]