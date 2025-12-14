from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
path('', views.index),
    path('populate/', views.populate_db),
    path('loadRS/', views.load_rs),
    path('mostListenedArtists/', views.most_listened_artists),
    path('mostFrequentTags/', views.most_frequent_tags),
    path('recommendedArtists/', views.recommended_artists),
    path('admin/', admin.site.urls),
    ]
