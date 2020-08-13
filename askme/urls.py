from django.urls import path
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path

from app import views


urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<tname>/', views.tag, name='tag'),
    path('question/<int:qid>/', views.question, name='question'),
    path('login/', views.login, name='login'),
    path('signup/', views.register, name='register'),
    path('ask/', views.ask, name='ask'),
    path('settings/', views.settings, name='settings'),
    path('admin/', admin.site.urls),
    path('logout/', views.logout, name='logout')
]
