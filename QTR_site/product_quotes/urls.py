from django.conf.urls import url
from . import views

app_name = 'product_quotes'
urlpatterns = [
    # ex: /languagebits/
    url(r'^generate_quote/$', views.generate_quote, name='generate_quote'),
    url(r'^view_all_quotes/$', views.view_all_quotes, name='view_all_quotes'),
    url(r'^view_quote/(?P<id>[0-9]+)/$', views.view_quote, name='view_quote'),
    url(r'^generate_license/(?P<id>[0-9]+)/(?P<launch_license>[0-9]+)/$', views.generate_license, name='generate_license'),
    url(r'^account_info/', views.account_info, name='account_info'),
    ]
