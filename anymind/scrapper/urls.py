from django.urls import path
from . import views

urlpatterns = [
    path('hashtags/<str:tag>', views.tweets_by_hashtag, name="tweets-by-tag"),
    path('users/<str:user>', views.user_tweets, name="tweets-by-user")
]
