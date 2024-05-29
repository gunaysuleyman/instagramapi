from django.urls import path
from .views import *

app_name = 'comments'

urlpatterns = [
    path('selencomment', FetchCommentsView.as_view(), name='selencomment'),
    path('apicomment', FetchCommentsApiView.as_view(), name='apicomment'),
    path('loadercomment', FetchCommentsLoaderView.as_view(), name='loadercomment'),
    path('lastcomment', FetchCommentsLastView.as_view(), name='lastcomment'),
    path('list', FetchCommentsApiView.as_view(), name='list'),
]
