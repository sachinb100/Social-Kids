# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from myapp.forms import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm
from django.contrib.auth.hashers import make_password,check_password
from myapp.models import UserModel,SessionToken,PostModel,LikeModel,CommentModel
from datetime import timedelta
from django.utils import timezone
from mysite.settings import BASE_DIR
from django.contrib import messages

from imgurpython import ImgurClient

import sendgrid
from sg import API_KEY,YOUR_CLIENT_ID,YOUR_CLIENT_SECRET
from sendgrid.helpers.mail import *


# Create your views here.

#For handling user's signup
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user_len=len(username)
            if user_len<4:
                print "User name should be atleast four character."
            # saving data to DB
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()
            return render(request, 'success.html')
    else:
        form = SignUpForm()

    return render(request, 'index.html', {'form': form})

#for handling user's login
def login_view(request):
    dict = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()
            if user:
                # Check for the password
                if not check_password(password, user.password):
                    dict['message'] = 'Incorrect Password! Please try again!'
                #Creating session for user if user is found
                else:
                    print "Login was successfull"
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
            else:
                print "Username is incorrect"
                dict['message'] = "Username is incorrect or user does not exist."
    else:
        form = LoginForm()
    dict['form'] = form
    return render(request, 'login.html', dict)

#for posting the image
def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                path = str(BASE_DIR +'/'+ post.image.url)


                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)

                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                success_message = 'Post can be submitted'
                return render(request, 'post.html', {'success_message': success_message})
                return redirect('/feed/')




        else:

            form = PostForm()



        return render(request, 'post.html', {'form' : form})
    else:
        return redirect('/login/')

#for handling feed of user
def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')



#to like the post
def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data.get('post')
            post_id = form.cleaned_data.get('post').id
            existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post_id=post_id, user=user)
                print "Post is liked"
                sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
                from_email =Email("scbhardwaj43@gmail.com")
                to_email = Email(post.user.email)
                subject = "InstaClone"
                content = Content("text/plain", "Your post is liked")
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
                print response
                print post.user.email
            else:
                existing_like.delete()
            return redirect('/feed/')
    else:
        return redirect('/login/')

#to comment on post
def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post=form.cleaned_data.get('post')
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()
            print "Comment is make on post"
            sg = sendgrid.SendGridAPIClient(apikey=API_KEY)
            from_email = Email("scbhardwaj43@gmail.com")
            to_email = Email(post.user.email)
            subject = "InstaClone"
            content = Content("text/plain", "Comment is make on  your post")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            print response
            print post.user.email
            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None