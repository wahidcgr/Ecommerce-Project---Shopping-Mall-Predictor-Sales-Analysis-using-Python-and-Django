from django.urls import path
from . import views
urlpatterns = [
    path('', views.index,name='index'),
    path('upload/',views.file_upload_view,name='upload'),
    path('analyse/',views.analyse,name='analyse'),
    path('pie_chart/',views.pie_chart_filter,name='pie_chart'),
    path('graph/',views.graph,name='graph'),
    path('bar_chart/',views.bar_chart,name='bar'),
    path('predict/',views.predict,name='predict'),
    
]