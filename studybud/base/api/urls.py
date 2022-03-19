from . import views 
from django.urls import path,include
from django.contrib import admin

urlpatterns = [
    path('',views.getRoutes),
    path('rooms/',views.getRooms),
    path('room/<str:pk>',views.getRoom),
]
