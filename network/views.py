from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
import time
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic import ListView
from network.models import *
from django.db.models import *
from django import forms

max_posts = 10


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if request.user.is_anonymous:
            return render(request, "network/login.html")
        else: 
            return redirect('index')



def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
	

def account_view(request, username):
    user = request.user      
    user_picture = User.objects.get(username=user)
    pictures = Picture.objects.filter(user=user_picture)
    pictures_count = pictures.count()
    if pictures_count == 0:
        picture = Picture.objects.get(id=12)
    else:
        sum = 0
        for picture in pictures:
            sum+=1
            if sum == 1:
                continue
    if request.method == 'GET':
        profile = User.objects.get(username=username)
        if request.user.is_anonymous:
            return redirect("login")
        if profile.username == user.username:
            return render(request, "network/account.html", {
			"form": PictureForm(),
            "picture": picture,
			"profile": profile,				
			})
        else:
            return redirect("index")
		
    else: 
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        
        profile = User.objects.get(username=username)
        profile.first_name = first_name
        profile.last_name = last_name        
        email_exist = User.objects.filter(email=email)
        if not email_exist or profile.email == email:
            profile.email = email
        else:
            return render(request, "network/account.html", {
			    "form": PictureForm(),
                "picture": picture,
			    "profile": profile, 				
				"message": "Email already taken"})        
        profile.save()        
        return render(request, "network/account.html",{
		    "message": "Account details has been updated successfully"})
		
		
def add_image(request):        
    user = request.user      
    user_picture = User.objects.get(username=user)
    pictures = Picture.objects.filter(user=user_picture)
    pictures_count = pictures.count()
    if pictures_count == 0:
        picture = Picture.objects.get(id=12)
    else:
        sum = 0
        for picture in pictures:
            sum+=1
            if sum == 1:
                continue
    if user.id is None:
        return redirect('login')		

    if request.method == 'GET':	    
        return render(request, "network/add_image.html", {
		    "picture": picture,
            "form": PictureForm()            
        })   
	
    else:    
        form = PictureForm(request.POST, request.FILES)
		
        if form.is_valid():               
            image = form.cleaned_data['image']
            imageCreated = Picture.objects.create( 
                user=request.user,			
                image=image
            )
            return render(request, "network/add_image.html",{
			    "form": form,
                "picture": picture,
                "imageCreated":imageCreated,
		        "message": "Image uploaded successfully"})            
            

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not username:
            return render(request, "network/register.html", {
                "message": "You must enter a username."})
        
        if not email:
            return render(request, "network/register.html", {
                "message": "You must enter an email."})

        if not password:
            return render(request, "network/register.html", {
                "message": "You must enter a password."})
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            email_exist = User.objects.filter(email=email)
            if not email_exist:
                user = User.objects.create_user(username, email, password)
                user.save()
            else:
                return render(request, "network/register.html", {
                "message": "Email has already been taken."
            })
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "*Username already taken."
            })
        login(request, user)
        return redirect("account_view", username)
    else:
        if request.user.is_anonymous:
            return render(request, "network/register.html")
        else:
            return redirect('index')


def index(request):
    user = request.user
    if not request.user.is_authenticated:
        picture = Picture.objects.get(id=12)
    else:
        user_picture = User.objects.get(username=user)
        pictures = Picture.objects.filter(user=user_picture)
        pictures_count = pictures.count()
        if pictures_count == 0:
            picture = Picture.objects.get(id=12)
        else:
            sum = 0
            for picture in pictures:
                sum += 1
                if sum == 1:
                    continue
    if request.user.is_authenticated:
        user = request.session["_auth_user_id"]
        likes = Like.objects.filter(post=OuterRef("id"), user_id=user)
        posts = Post.objects.filter().order_by("-date").annotate(current_like=Count(likes.values("id")))
    else:
        posts = Post.objects.order_by("-date").all()
    paginator = Paginator(posts, max_posts)
    page_no = request.GET.get("page")
    post_items = paginator.get_page(page_no)
    return render(request, "network/index.html", {
        "posts": post_items,
        "picture": picture,
        "form": NewPost(),
        "edit_post": EditPost()
    })


def following(request):
    user = request.user      
    user_picture = User.objects.get(username=user)
    pictures = Picture.objects.filter(user=user_picture)
    pictures_count = pictures.count()
    if pictures_count == 0:
        picture = Picture.objects.get(id=12)
    else:
        sum = 0
        for picture in pictures:
            sum+=1
            if sum == 1:
                continue
    if request.user.is_authenticated:
        user = request.session['_auth_user_id']
        followers = Follower.objects.filter(follower=user)
        likes = Like.objects.filter(post=OuterRef('id'), user_id=user)
        posts = Post.objects.filter(user_id__in=followers.values('following_id')).order_by(
            "-date").annotate(current_like=Count(likes.values('id')))
    else:
        return HttpResponseRedirect(reverse("login"))

    paginator = Paginator(posts, max_posts)
    page_no = request.GET.get('page')
    post_items = paginator.get_page(page_no)
    return render(request, "network/following.html", {
        "posts": post_items,
        "picture": picture,
        "form": NewPost()
    })


def follow(request, id):
    try:
        sequel = 'follow'
        user = User.objects.get(id=request.session['_auth_user_id'])
        fan = User.objects.get(id=id)
        follower = Follower.objects.get_or_create(follower=user, following=fan)
        if not follower[1]:
            Follower.objects.filter(follower=user, following=fan).delete()
            sequel = 'unfollow'
        followers = Follower.objects.filter(following=fan).count()
    except KeyError:
        return HttpResponseBadRequest("Bad Request: There are no followers")
    return JsonResponse({
	    "sequel": sequel, 
	    "total_followers": followers
	})
    
    
def post_message(request):

    if request.method == "POST":
        form = NewPost(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.session['_auth_user_id'])            
            text = form.cleaned_data["post_text"]
            post = Post(user=user, text=text)
            post.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return HttpResponseRedirect(reverse("index"))


def editpost(request, id):
    if request.is_ajax and request.method == "POST":
        form = EditPost(request.POST)
        if form.is_valid():
            text = form.cleaned_data["edit_text"]
            Post.objects.filter(
                id=id, user_id=request.session['_auth_user_id']).update(text=text)
            return JsonResponse({"result": 'ok', 'text': text})
        else:
            return JsonResponse({"error": form.errors}, status=400)

    return JsonResponse({
	    "error": HttpResponseBadRequest("Bad Request: no like chosen")}, 
		status=400
	)
	

def delete_post(request, post):
    if request.method == 'POST':
        post = Post.objects.get(id=post)
        post.delete()
        return HttpResponse('success')
		
		
def like(request, id):

    try:
        like_class = 'fas fa-heart'
        user = User.objects.get(id=request.session['_auth_user_id'])
        post = Post.objects.get(id=id)
        like = Like.objects.get_or_create(user=user, post=post)
        if not like[1]:
            like_class = 'far fa-heart'
            Like.objects.filter(user=user, post=post).delete()

        total_likes = Like.objects.filter(post=post).count()
    except KeyError:
        return HttpResponseBadRequest("Bad Request: There is no like")
    return JsonResponse({
        "like": id, 
		"like_class": like_class, 
		"total_likes": total_likes
    })


def profile(request, username):
    person_count=0
    profile_account = User.objects.get(username=username)    
    user_picture = User.objects.get(username=profile_account)
    pictures = Picture.objects.filter(user=user_picture)
    pictures_count = pictures.count()
    if pictures_count == 0:
        picture = Picture.objects.get(id=12)
    else:
        sum = 0
        for picture in pictures:
            sum+=1
            if sum == 1:
                continue
    if request.user.is_authenticated:
        access_user = request.session["_auth_user_id"]
        person_count = Follower.objects.filter(follower=access_user, following=profile_account).count()
        likes = Like.objects.filter(post=OuterRef("id"), user_id=access_user)
        posts = Post.objects.filter(user=profile_account).order_by("-date").annotate(current_like=Count(likes.values("id")))
    else:
        posts = Post.objects.filter(user=profile_account).order_by("-date").all()
    
    following = Follower.objects.filter(follower=profile_account)
    follower = Follower.objects.filter(following=profile_account)    
    following_count = Follower.objects.filter(follower=profile_account).count()
    followers = Follower.objects.filter(following=profile_account).count()

    paginator = Paginator(posts, max_posts)
    page_no = request.GET.get('page')
    post_items = paginator.get_page(page_no)
    return render(request, "network/profile.html", {
        "profile_account": profile_account,
        "picture": picture,
		"posts": post_items, 
		"post_count": posts.count(),
		"person_count": person_count, 
        "following": following,
        "follower": follower,
		"following_count": following_count, 
		"followers": followers, 
		"form": NewPost(), 
		"edit_post": EditPost()
    })
		
		
class NewPost(forms.Form):    
    post_text = forms.Field(widget=forms.Textarea(
        {"rows": "3", 
		"maxlength": 300, 
		"class": "form-control", 
		"placeholder": "What's on your mind?"
		}), label="New Post", required=True)


class EditPost(forms.Form):    
    edit_text = forms.Field(widget=forms.Textarea(
        {"rows": "3",
		"maxlength": 300, 
		"class": "form-control", 
		"placeholder": "What's on your mind?", 
		"id": "edit_text"
		}), label="New Post", required=True)
		
class PictureForm(forms.ModelForm):
    """Image Model Form for processing images"""
    class Meta:
        model = Picture        
        fields = ('image',)
             
                   

    			   

