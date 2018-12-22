from django.urls import path
from Transfer import views

urlpatterns = [
    path('', views.import_and_compare_handler, name='import_and_compare_handler')
]
