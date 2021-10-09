from django.urls import path

from . import views

urlpatterns = [
    path(r'testapi/', views.testapi, name='testapi'),
]