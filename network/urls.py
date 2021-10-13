
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("like/<int:id>", views.like, name="like"),
    path("editpost/<int:id>", views.editpost, name="editpost"),	
	path("delete_post/<str:post>", views.delete_post, name="delete_post"),
    path("follow/<int:id>", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("post_message", views.post_message, name="post_message"),    
    path("profile/<str:username>", views.profile, name="profile"),
	path("add_image", views.add_image, name="add_image"),
    path("account/<str:username>", views.account_view, name="account_view")	
]

