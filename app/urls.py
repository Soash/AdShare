from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('save/', views.save, name='save'),
    path('post/', views.post, name='post'),
    path('earn/', views.earn, name='earn'),
    path('<str:username>/<str:post_char>/ad/', views.adpage, name='adpage'),
    path('<str:username>/<str:claim_char>/claim/', views.claim, name='claim'),
]

