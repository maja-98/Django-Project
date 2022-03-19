from email import message
import os
from pydoc_data.topics import topics
from django.shortcuts import render,redirect
from .models import Room,Topic,Message
from .forms import RoomForm,MessageForm,UserForm,MyUserCreationForm
from django.http import HttpResponse
from django.db.models import Q
from .models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages  
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.

def loginPage(request):
    
    page= 'login'
    if request.user.is_authenticated:
        return redirect('home')
    context={'page':page}
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user= User.objects.get(email=email)
            
        except:
            messages.error(request,'User does not exist')  
        user= authenticate(request,email=email, password=password) 
        if user :
            login(request,user)
            return redirect ('home')
        else:
            messages.error(request,'Username or password does not exist')
    return render (request, 'base/login_register.html',context)

def registerUser(request):
    page='Register'
    form= MyUserCreationForm()
    if request.method=='POST':

        form= MyUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username= user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'An error occured during registration')
    
    return render (request, 'base/login_register.html',{'page':page,'form':form} )

def logoutUser(request):
    logout(request)
    return redirect('home')
    

def home(request):

    q= request.GET.get('q') if request.GET.get('q')!=None else ''
    #Model__parentroot__howtosearch ;icontain is case nsensitive and contain is case sensitive

    
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q)|
        Q(description__icontains=q))
    topics=Topic.objects.all()[:5]
    room_messages= Message.objects.filter(
        Q(room__topic__name__icontains=q) )[:10]

    room_count=rooms.count()
    return render(request, 'base/home.html',{'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages})

def room(request,pk):
    
    current_room=Room.objects.get(id=pk)
    participants= current_room.participants.all()
    room_messages = current_room.message_set.all().order_by('-created')
    if request.method=='POST':
        message=Message.objects.create(
            user=request.user,
            room=current_room,
            body=request.POST.get('body')
        )
        current_room.participants.add(request.user)
        return redirect('room',pk=current_room.id)
    context= {'room':current_room,'room_messages':room_messages,'participants':participants}
    return render(request, 'base/room.html',context) 

def userprofile(request,pk):
    q= request.GET.get('q') if request.GET.get('q')!=None else ''
    user= User.objects.get(id=pk)
    rooms = user.room_set.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q)|
        Q(description__icontains=q))
    messages = user.message_set.filter(
        Q(room__topic__name__icontains=q) )[:10]
    topics=Topic.objects.all()
    context={'user':user,'rooms':rooms,'room_messages':messages,'topics':topics,'name':'profile','pk':pk}
    return render (request, 'base/profile.html',context)
    
@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics= Topic.objects.all()
    if request.method == 'POST':
        topic_name =request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST)
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        
        return redirect('home')
    context = {'form' : form ,'topics':topics}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login')
def updateRoom(request,pk):
    topics= Topic.objects.all()
    room = Room.objects.get(id=pk) 
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')
    if request.method == 'POST':
        topic_name =request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST)
        
        room.name=request.POST.get('name')
        room.topic=topic
        room.host=request.user
        room.description =  request.POST.get('description')
        
        room.save()
        return redirect('home')

    context = {'form' : form, 'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)

@login_required(login_url='/login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk) 
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')
    if request.method == 'POST':
        room.delete()
        return redirect ('home') 
    return render(request,'base/delete_form.html',{'term':'Room','obj':room})
    
@login_required(login_url='/login')   
def deleteMessage(request,rk,pk):
    message = Message.objects.get(id=pk) 
    if request.user != message.user:
        return HttpResponse('{} You are not allowed here!!!, only {} can delete'.format(request.user,message.user))
    if request.method == 'POST':
        message.delete()
        if rk=='home':
            return redirect ('home')
        return redirect ('/room/'+str(rk)) 
    return render(request,'base/delete_form.html',{'term':'Message','obj':message})
    
    form = RoomForm(instance=room)
@login_required(login_url='/login')
def updateUser(request):
    form = UserForm(instance=request.user)
    if request.method =='POST':
        old_profile=request.user.avatar
        form= UserForm(request.POST ,request.FILES,instance=request.user)
        if form.is_valid():
            form.save()
            new_profile=request.user.avatar
            if old_profile != new_profile:
                os.remove(str(BASE_DIR)+ '/static/images/'+str(old_profile))
            return redirect('profile',pk=request.user.id)
    return render(request, 'base/update-user.html',{'form':form})

def topicsPage(request,pk):
    q= request.GET.get('q') if request.GET.get('q')!=None else ''
    topics=Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html',{'topics':topics,'pk':pk})

def activityPage(request):
    room_messages= Message.objects.all()
    return render(request, 'base/activity.html' ,{'room_messages':room_messages})

def deleteUser(request):
    if request.method =='POST':
        password=request.POST.get('password')
        user= authenticate(request,email=request.user.email, password=password) 
        if user :
            if str(request.user.avatar) != 'avatar.svg':
                os.remove(str(BASE_DIR)+ '/static/images/'+str(request.user.avatar))
            request.user.delete()
            return redirect ('/login')
        else:
            messages.error(request,'Username or password does not exist')       
        
        
    return render(request,'base/delete_form.html',{'term':'delete_user'})
    
    