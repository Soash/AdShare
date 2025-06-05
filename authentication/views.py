from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from adshare import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from . tokens import generate_token
from django.contrib.auth.decorators import login_required

def home(request):
    if request.user.is_authenticated:
        fname = request.user.first_name
    else:
        fname = "Guest" 
    return render(request, 'home.html', {"fname":fname,})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist!")
            return redirect('signup')
        
        if User.objects.filter(email=email):
            messages.error(request, "Email Already Registered!")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't matched!")
            return redirect('signup')

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.is_active = False
        # myuser.is_active = True
        myuser.save()

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email - Adshare"
        message2 = render_to_string('auth/activation_mail.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently = True
        email.send()

        messages.error(request, "Please check you mail to activate your account.")
        return redirect('home')

    return render(request, 'auth/signup.html')

def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('signin')
    else:
        return render(request, 'auth/activation_failed.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!")
            return redirect('home')
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')
    return render(request, 'auth/signin.html')

def signout(request):
    logout(request)
    messages.error(request, "Logged Out Successfully!")
    return redirect('home')

def forgot(request):
    if request.method == "POST":
        email = request.POST['email']        
        if not User.objects.filter(email=email):
            messages.error(request, "Email Not Registered!")
            return redirect('signup')

        myuser = User.objects.get(email=email)

        current_site = get_current_site(request)
        email_subject = "Reset your password - Adshare"
        message2 = render_to_string('auth/reset_mail.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser),
        })
        email = EmailMessage(email_subject, message2, settings.EMAIL_HOST_USER, [myuser.email],)
        email.fail_silently = True
        email.send()

        messages.success(request, "Please check your mail to reset.")
        return redirect('forgot')
    else:
        return render(request, 'auth/forgot.html')
    
def reset(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        return render(request, 'auth/reset.html',{'username':myuser.username})
    else:
        return render(request,'auth/reset_failed.html')

def savePass(request):
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!")
            return redirect('reset')
        try:
            user = User.objects.get(username=username)
            user.set_password(pass1)
            user.save()
            messages.success(request, "Password Changed!")
            return redirect('signin')
        except User.DoesNotExist:
            messages.error(request, "User not found!")
            return redirect('reset')
    else:
        return redirect('signin')
    
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        username = user.username
        password = request.POST.get('password')

        # Check if the provided password is correct
        auth_user = authenticate(username=username, password=password)
        if auth_user is not None:
            # Password is correct, delete the account
            user.delete()
            logout(request)
            messages.success(request, 'Your account has been deleted successfully.')
            return redirect('home')  # Redirect to your home page or any other page
        else:
            # Password is incorrect
            messages.error(request, 'Incorrect password. Please try again.')

    return render(request, 'auth/delete_account.html') 

def custom_404(request, exception):
    return render(request, 'auth/404.html', status=404)