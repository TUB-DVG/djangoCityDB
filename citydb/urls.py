from django.urls import path
from citydb.views import views

urlpatterns = [
    path('', views.index, name='index'),
]
