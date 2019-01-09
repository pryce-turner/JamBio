from django.urls import path, include
from QC import views

urlpatterns = [
    path('run_qc', views.run_qc_handler, name='run_qc_handler'),
    path('reports', views.list_projects),
    path('reports/<str:proj_id_hash>/', views.show_report, name='show_report')
]
