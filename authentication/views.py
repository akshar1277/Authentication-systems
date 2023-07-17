from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from gfg import settings
from django.core.mail import send_mail ,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, 'authentication/index.html')

def rlogin(request):
    return redirect('signin')


def signup(request):

    if request.method == "POST":
        username = request.POST.get('username')
        fname = username = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('Email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')


        if User.objects.filter(username=username):
            messages.error(request,"username already exist please try some other username")
            return redirect('signin')

        if User.objects.filter(email=email):
            messages.error(request,"Email alredy registred")
            return redirect('signin')
 
        if len(username)>10:
            messages.error(request,"username must be under 10 characters")

        if pass1 != pass2:
            messages.error(request,"password didn't match ")

        if not username.isalnum():
            messages.error(request,"username must be alpha numeric")
            return redirect('signin')

        myuser = User.objects.create_user(username, email, pass1)
        
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active=False

        myuser.save()

        messages.success(request, "your account has been successfully created. We have sent you a conformation email please confirm your email in order to activate your account")
        



        #welcome email

        subject="welcome to LdceClgNetwork"
        message= "hello" + myuser.first_name + "!! \n" "welcome to LdceClgNetwork !! \n thank you for visiting our website \n We have also sent you a confirmation email ,please confirm your email address in order to activate your account \n\n Thanking you \n  anubhav madhav"
        from_email=settings.EMAIL_HOST_USER
        to_list=[myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)


        #email address confirmation email 

        current_site=get_current_site(request)
        email_subject = "confirm your email @ ldceclgnetwork !!"
        message2=render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser),
        })
 
        email=EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently=True
        email.send()










        return redirect('signin')

    return render(request, 'authentication/register.html')

def signin(request):

    if request.method == "POST":
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname': fname})
        else:
            messages.error(request, " bad credentials!")
            return redirect('signin')
    return render(request, 'authentication/login.html')



def signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect('signin')


def activate(request,uidb64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uidb64))
        myuser=User.objects.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoseNotExist):
        myuser=None

    if myuser is not None and  generate_token.check_token(myuser,token):
        myuser.is_active=True
        myuser.save()
        login(request,myuser)
        messages.success(request, "your account has been successfully activated.")
        return redirect('signin')

    else:
        return render(request,'activation_failed.html')
    
    return redirect('home')
