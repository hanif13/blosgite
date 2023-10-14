from django.shortcuts import render,redirect
from .form import userRegForm, LoginForm, UserProfileUpdateForm,ProfilePictureUpdateForm
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from .decoretors import *
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from notifications.models import Notification
from .models import *
# Create your views here.


@never_cache
@not_logged_in_required
def registration_user(request):
    form = userRegForm()
    if request.method == "POST":
        form = userRegForm(request.POST)
        if form.is_valid():
            user =  form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            messages.success(request,"Registration Succesful")
            return redirect('login')
        else:
            print(form.errors)
    context = {
        'form':form
    }
    return render(request,'registration.html',context)


@never_cache
@not_logged_in_required
def login_user( request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username = form.cleaned_data.get('username'),
                password = form.cleaned_data.get('password')
            )
            if user:
                login(request,user)
                return redirect('/')
                
            else:
                messages.warning(request,"Wrong username or password")
        print(messages.error)
    return render(request,'login.html',context={'form':form})

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request):
    account = User.objects.get(pk=request.user.pk)
    form = UserProfileUpdateForm(instance=account)
    if request.method == "POST":
        if request.user.pk != account.pk:
            return redirect('home')
        form = UserProfileUpdateForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request,"Profile has been Updated sucessfully")
            return redirect('profile')
        else:
            print(form.errors)
    context={
        'account':account,
        'form':form
    }
    return render(request, 'profile.html',context)


@login_required(login_url='login')
def change_profile_picture(request):
    if request.method == "POST":
        form = ProfilePictureUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            image = request.FILES['profile_image']
            user = User.objects.get(pk=request.user.pk)
            if request.user.pk != user.pk:
                return redirect('home')
            
            user.profile_image= image
            user.save()
            messages.success(request,"Profile picture updated sucessfully")
            return redirect('profile')

def view_user_information(request,username):
    account = User.objects.get(username=username)
    following =  False
    muted = None
    
    if request.user.is_authenticated:
        
        if request.user.id == account.id:
            return redirect('profile')
        
        followers = account.followers.filter(
        followed_by__id = request.user.id
        )
        if followers.exists():
            following = True
        
    if following:
        queryset = followers.first()
        if queryset.muted:
            muted=True
        else:
            muted = False
            
    context={
        'account':account,
        'following':following,
        'muted':muted
    }
    return render(request,'user-information.html', context)

@login_required(login_url='login')
def follow_or_unfolow_user(request,user_id):
    followed = User.objects.get(id=user_id)
    followed_by = User.objects.get(id=request.user.id)

    follow , created = Follow.objects.get_or_create(
        followed = followed,
        followed_by = followed_by
    )
    
    if created:
        followed.followers.add(follow)
        

    else:
        followed.followers.remove(follow)
        follow.delete()

    return redirect("view_user_information", username = followed.username)

@login_required(login_url='login')
def user_notifications(request):
    notifications = Notification.objects.filter(
        user = request.user,
        is_seen = False
    )
    for notification in notifications:
        notification.is_seen = True
        notification.save()
    return render(request,'notifications.html')

@login_required(login_url='login')
def mute_or_unmute(request,user_id):
    user = User.objects.get(pk=user_id)
    follower = User.objects.get(pk=request.user.pk)
    instance = Follow.objects.get(
        followed = user,
        followed_by = follower
    )
    
    if instance.muted:
        instance.muted = False
        instance.save()

    else:
        instance.muted = True
        instance.save()

    return redirect('view_user_information', username = user.username)
    



