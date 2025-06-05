import random, string, re
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ClaimURL, Script, PostURL
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum



#Porfile
##############################################################################################################
@login_required(login_url='signin')
def profile(request):
    try:
        scripts = Script.objects.filter(user=request.user)

        total_tokens = PostURL.objects.filter(user=request.user).aggregate(total_tokens=Sum('token'))['total_tokens'] or 0
        token = total_tokens if total_tokens else '💵'

        return render(request, 'app/profile.html', {'scripts': scripts,'token':token})
    except:
        return render(request, 'app/profile.html')
##############################################################################################################



#save
##############################################################################################################  
@login_required(login_url='signin')
def save(request):
    if request.method == 'POST':
        textarea1 = request.POST.get('textarea1')
        textarea2 = request.POST.get('textarea2')
        textarea3 = request.POST.get('textarea3')
        textarea4 = request.POST.get('textarea4')

        existing_script = Script.objects.filter(user=request.user).first()
        if existing_script:
            existing_script.textarea1 = textarea1
            existing_script.textarea2 = textarea2
            existing_script.textarea3 = textarea3
            existing_script.textarea4 = textarea4
            existing_script.save()
        else:
            Script.objects.create(
                user=request.user,
                textarea1=textarea1,
                textarea2=textarea2,
                textarea3=textarea3,
                textarea4=textarea4,)
        messages.success(request, "Saved!")     
        return redirect('profile')
##############################################################################################################



#post
##############################################################################################################
@login_required(login_url='signin')
def post(request):

    post_char = randChar()
    while PostURL.objects.filter(post_char=post_char).exists():
        post_char = randChar()
    claim_char = randChar()
    while PostURL.objects.filter(claim_char=claim_char).exists():
        claim_char = randChar()

    try:
        user = Script.objects.get(user=request.user)
        if user.coin >= 10:
            PostURL.objects.create(user=request.user, post_char=post_char, claim_char=claim_char)
            user.coin -= 10
            user.save()
            return redirect('profile')
        else:
            messages.error(request, 'Not Enough Coin!')
            return redirect('earn')
    except:
        return redirect('profile')
##############################################################################################################



#earn
##############################################################################################################
@login_required(login_url='signin')
def earn(request):

    all_urls = PostURL.objects.all()
    claimed_urls = ClaimURL.objects.values_list('posted_url_id', flat=True)
    unclaimed_urls = all_urls.exclude(id__in=claimed_urls).exclude(user=request.user)

    scripts = Script.objects.filter(user=request.user).first()
    if scripts:
        coin = scripts.coin
    else:
        coin = '🪙'
            
    total_tokens = PostURL.objects.filter(user=request.user).aggregate(total_tokens=Sum('token'))['total_tokens'] or 0
    token = total_tokens if total_tokens else '💵'

    base_url = request.build_absolute_uri('/')
    return render(request, 'app/earn.html', {'posted_urls': unclaimed_urls, 'base_url': base_url, 'coin':coin, 'token':token})
##############################################################################################################



#adpage
##############################################################################################################
@login_required(login_url='signin')
def adpage(request, username, post_char):

    post_url = PostURL.objects.get(user__username=username, post_char=post_char)
    user = post_url.user
    claim_char = post_url.claim_char

    user = Script.objects.get(user__username=username).user
    existing_script = Script.objects.get(user=user)
    t1 = existing_script.textarea1
    t2 = existing_script.textarea2
    t4 = existing_script.textarea4
    t3s, t3d = native_banner(existing_script.textarea3)
    context = {
        'user': user,
        'claim_char': claim_char,
        'popunder': scriptParse(t1),
        'direct_link': t2,
        'social_bar': scriptParse(t4),
        'nb_s': t3s,
        'nb_d': t3d,
    }
    return render(request, 'app/ad.html', context=context)
##############################################################################################################



#claim
##############################################################################################################
@login_required(login_url='signin')
def claim(request, username, claim_char):
    try:
        with transaction.atomic():
            posted_url = PostURL.objects.select_related('user').get(user__username=username, claim_char=claim_char)

            if ClaimURL.objects.filter(user=request.user, claim_char=claim_char).exists():
                messages.error(request, 'Already Claimed')
                return redirect('earn')

            ClaimURL.objects.create(user=request.user, claim_char=claim_char, posted_url=posted_url)

            user1 = Script.objects.get(user=request.user)
            user1.coin += 1
            user1.save()

            posted_url = PostURL.objects.get(user__username=username, claim_char=claim_char)
            posted_url.token -= 1
            posted_url.save()
            if posted_url.token == 0:
                posted_url.delete()
        return redirect('earn') 
    except Exception as e:
        messages.error(request, 'Error occurred while claiming. Please try again.')
        return redirect('earn')
##############################################################################################################



def randChar():
    characters = string.ascii_letters + string.digits
    x = ''.join(random.choice(characters) for i in range(6))
    return x

def scriptParse(script):
    x = script
    src_value  = re.search(r"src='(//[^']+)'", x).group(1)
    return src_value

def native_banner(script):
    text = script
    match1 = re.search(r"//[^']+?\.js", text).group()
    match2 = re.search(r'container-([^"]+)', text).group()

    return match1, match2