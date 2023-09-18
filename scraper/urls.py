from django.urls import path, include
from scraper.views import *

urlpatterns = [
    path('', home, name='home'),
    path('scrape_now', scrape_now, name='scrape_now'),
]