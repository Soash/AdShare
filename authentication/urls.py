from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgot/', views.forgot, name='forgot'),
    path('reset/<uidb64>/<token>', views.reset, name='reset'),
    path('savePass/', views.savePass, name='savePass'),
    path('delete-account/', views.delete_account, name='delete_account'),
]