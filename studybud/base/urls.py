from django.urls import path
from . import views


urlpatterns = [
    path('', views.home,name='home'),
    path('room/<int:pk>/',views.room,name='room'),
    path('create-room/',views.createRoom,name='create-room'),
    path('update-room/<str:pk>',views.updateRoom,name='update-room'),
    path('delete-room/<str:pk>',views.deleteRoom,name='delete-room'),
    path('login/',views.loginPage,name='login'),
    path('register/',views.registerUser,name='register'),
    path('logout/',views.logoutUser,name='logout'),
    path('delete-message/<str:rk>/<str:pk>/',views.deleteMessage,name='delete-message'),
    path('profile/<str:pk>/',views.userprofile,name='profile'),
    path('update-user/',views.updateUser,name='update-user'),
    path('topics/<str:pk>/',views.topicsPage,name='topics'),
    path('activities/',views.activityPage,name='activities'),
    path('delete-user/',views.deleteUser,name='delete-user'),

]