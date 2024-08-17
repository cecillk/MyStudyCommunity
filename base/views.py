from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from django.contrib.auth.decorators import login_required 
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse




# Create your views here.

# rooms = [
#   {'id' : 1, 'name' : 'Lets learn python!'}, 
#   {'id' : 2, 'name' : 'Design with me'}, 
#   {'id' : 3, 'name' : 'Front end Developers!'}, 
#]


def loginPage(request):
    # Set the page variable to 'login'
    page = 'login'

    # Redirect to home if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('home')

    # Process the form if the request method is POST
    if request.method == 'POST':    
        # Get username and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            # Check if the user exists in the database
            user = User.objects.get(username=username)      
        except User.DoesNotExist:
            # Show error if the user does not exist
            messages.error(request, 'User does not exist')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log the user in and redirect to home
            login(request, user)
            return redirect('home')
        else:
            # Show error if username or password is incorrect
            messages.error(request, 'Username or password is incorrect')
 
    # Render the login page with context
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    # Log out the current user
    logout(request)
    
    # Redirect to the home page
    return redirect('home')



def registerPage(request):
    # Set the page variable to 'register'
    page = 'register'
    
    # Initialize an empty registration form
    form = UserCreationForm()
    
    # Process the form if the request method is POST
    if request.method == 'POST':
        # Create a form instance with the submitted data
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            # Save the new user but don't commit to the database yet
            user = form.save(commit=False)
            # Convert username to lowercase
            user.username = user.username.lower()
            # Save the user to the database
            user.save()
            # Log the user in and redirect to home
            login(request, user)
            return redirect('home')
        else:
            # Show an error message if the form is not valid
            messages.error(request, 'An error occurred during registration.')

    # Create a context dictionary to pass data to the template
    context = {'form': form, 'page': page}

     # Render the registration page with the form and page context
    return render(request, 'base/login_register.html', context)



def home(request):
    # Get the search query from the request, default to an empty string if not provided
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    
    # Filter rooms based on the search query, checking topic name, room name, and description
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    
    # Get all topics
    topics = Topic.objects.all()[0:5]
    
    # Count the number of rooms that match the search query
    room_count = rooms.count()
    
    # Filter messages based on the search query, checking room topic name
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    # Create a context dictionary to pass data to the template
    context = {
        'rooms': rooms,                 # List of rooms that match the search query
        'topics': topics,               # List of all topics
        'room_count': room_count,       # Total count of rooms that match the search query
        'room_messages': room_messages  # List of messages related to the search query
    }
    
    # Render the home page with the context data
    return render(request, 'base/home.html', context)



def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)
    
    context = {'room' : room, 'room_messages' : room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    # Initialize an empty form instance for creating a new room
    form = RoomForm()

    topics = Topic.objects.all()
    
    # Check if the request method is POST, indicating form submission
    if request.method == 'POST':
        # Create a form instance with the submitted data
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic=topic, 
            name=request.POST.get('name'),
            description=request.POST.get('description'),

        )
        return redirect('home')

    # Create a context dictionary to pass the form instance to the template
    context = {'form': form, 'topics':topics}
    
    # Render the form template with the context data
    return render(request, 'base/room_form.html', context)

def userProfile(request, pk):
    user = User.objects.get(id = pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'topics':topics, 'room_messages':room_messages}
    return render(request, 'base/profile.html', context)

@login_required(login_url = 'login')    
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')


    context = {'form' : form, 'topics':topics, 'room' : room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here') 

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : room})


@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here') 

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj' : message})


@login_required(login_url = 'login')
def updateUser(request):
    
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics':topics})




def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})



