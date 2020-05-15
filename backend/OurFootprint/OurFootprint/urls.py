"""back_end URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from . import views

from django.contrib import admin
admin.autodiscover()

# reroute all the requests to users endpoint to the users app
urlpatterns = [
    path('api/endpoint1', views.index, name='index'),
    path('api/endpoint2', views.e2, name='e2'),
    path('api/users/', include('users.urls')),

    path('api/fortis/', include('utility.urls')),

    # path('api/fortis/', views.fortis_bill, name='upload fortis bill/ get previous fortis bills'),
    # path('api/fortis/<int:pk>/', views.fortis_bill, name='upload fortis bill/ get previous fortis bills'),

    path('api/hydro/', views.hy, name='upload hydro bill/ get previous hydro bills'),
    path('api/hydro/<int:pk>/', views.hydro_bill, name='upload hydro bill/ get previous hydro bills'),

    path('api/commute/', views.add_commute, name='add a commute/ get all commutes'),
    path('api/commute/<int:pk>/', views.add_commute, name='add a commute/ get all commutes'),

    path('api/vehicles/', views.get_vehicles_json, name="get vehicles in json format"),
    path('api/calculate/', views.calculate_footprint, name="calculate the carbon footprint for this user"),
    path('api/signup/', views.register, name="Signup user"),
    path('api/logout/', views.sign_out, name="Logout user"),
    path('api/login/', views.sign_in, name="Sign in user"),
    # TODO: Remove for production
    url(r'^admin/', admin.site.urls),
]
