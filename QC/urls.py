from django.urls import path, include
from QC import views

#router = routers.DefaultRouter()
#router.register('test', views.rest_test)

urlpatterns = [
    path('run_qc', views.run_qc_handler, name='run_qc_handler'),
    path('reports', views.list_projects),
    path('reports/<str:order_id_hash>/', views.show_report, name='show_report')
]
