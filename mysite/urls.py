"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import login_view,post_view,signup_view,feed_view,like_view,comment_view,upvote_view,particular_view

urlpatterns = [
    url('post/', post_view),
    url('login/',login_view),
    url('feed/', feed_view),
    url('like/', like_view),
    url('comment/', comment_view),
    url('upvote/', upvote_view),
    # url(r'^feed/(<username>)$',particular_view,name="username"),
    url(r'^feeds/(?P<name>[\w.@+-]+)$',particular_view),

    url('',signup_view)
]
