import time
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from codefisher_apps.pastelsvg.models import Icon, PastelSVGDonation, ProtectedDownload, IconRequest, IconRequestComment, UseExample
from haystack.query import SearchQuerySet
from django.http import HttpResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse
from djangopress.donate.views import DonationPayPalPaymentsForm
from django.core.urlresolvers import reverse
from django.conf import settings
from djangopress.core.util import has_permission, get_client_ip
from codefisher_apps.downloads.models import Download, DownloadGroup
from django import forms
from django.contrib import messages
# we use the same fields so this works
from djangopress.forum.views import check_askmet_spam
from django.contrib.auth.decorators import login_required

def index(request):
    icon_group, icons = get_download('pastel.svg@codefisher.org')
    icon_group_large, icons_large = get_download('pastel.svg.large@codefisher.org')
    data = {
            "icon_group": icon_group,
            "icons": icons,
            "icon_group_large": icon_group_large,
            "icons_large": icons_large,
        "title": "Pastel SVG Icon Set"
    }
    return render(request, 'pastelsvg/index.html' , data)

class RequestForm(forms.ModelForm):
    class Meta(object):
        fields = ('title', 'message', 'concept_icon')
        model = IconRequest
        
class RequestAnonymousForm(forms.ModelForm):
    class Meta(object):
        fields = ('title', 'message', 'concept_icon', 'poster_name', 'poster_email')
        model = IconRequest
        
    def __init__(self, *args, **kwargs):
        super(RequestAnonymousForm, self).__init__(*args, **kwargs)
        self.fields['poster_name'].required = True
        self.fields['poster_email'].required = True
        
class IconRequestCommentForm(forms.ModelForm):
    class Meta(object):
        fields = ("message", )
        model = IconRequestComment
    
    def __init__(self, *args, **kwargs):
        super(IconRequestCommentForm, self).__init__(*args, **kwargs)
        self.fields['message'].widget = forms.Textarea(attrs={'rows':3})
        
class IconRequestCommentAnonymousForm(IconRequestCommentForm):
    class Meta(object):
        fields = ("poster_name", "poster_email", "message")
        model = IconRequestComment
    
    def __init__(self, *args, **kwargs):
        super(IconRequestCommentAnonymousForm, self).__init__(*args, **kwargs)
        self.fields['poster_name'].required = True
        self.fields['poster_email'].required = True
        
class UseExampleForm(forms.ModelForm):
    class Meta(object):
        fields = ("title", "url", "description")
        model = UseExample
    
       
class UseExampleAnonymousForm(UseExampleForm):
    class Meta(object):
        fields = ("poster_name", "poster_email", "title", "url", "description")
        model = UseExample
    
    def __init__(self, *args, **kwargs):
        super(UseExampleAnonymousForm, self).__init__(*args, **kwargs)
        self.fields['poster_name'].required = True
        self.fields['poster_email'].required = True
        
def who_uses(request, page=1):
    if request.method == "POST":
        form = choose_form(request, UseExampleForm, UseExampleAnonymousForm, request.POST)
        if form.is_valid():
            use_example = form.save(commit=False)
            use_example.ip = get_client_ip(request)
            if request.user.is_authenticated():
                use_example.poster = request.user
            use_example.save()
            messages.add_message(request, messages.SUCCESS, "Your project has been submitted, it will be made public after being reviewed.")
            return redirect(reverse('pastel-svg-who-uses'))
    else:
        form = choose_form(request, UseExampleForm, UseExampleAnonymousForm)
    use_example = UseExample.objects.filter(validated=True).order_by('-posted')  
    paginator = Paginator(use_example, 20)    
    try:
        use_page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        if page != 1 and use_example:
            return redirect(use_example[0].get_absolute_url(paginator.num_pages))
    data = {
        "title": "Who Uses Pastel SVG Icons",
        "form": form,
        "page": use_page,
        "use_example": use_example[0] if use_example else None,
    }
    return render(request, 'pastelsvg/use_example.html' , data)

def choose_form(request, authenticated, anonymous, *args, **kargs):
    if request.user.is_authenticated():
        return authenticated(*args, **kargs)
    return anonymous(*args, **kargs)
        
def make_icon_request(request):
    if request.method == "POST":
        form = choose_form(request, RequestForm, RequestAnonymousForm, request.POST)
        if form.is_valid():
            icon_request = form.save(commit=False)
            icon_request.ip = get_client_ip(request)
            if request.user.is_authenticated():
                icon_request.poster = request.user
            icon_request.is_spam = check_askmet_spam(request, form)
            icon_request.save()
            if icon_request.is_spam:
                data = {
                        "title": "Request flagged as Spam",
                        "message": "We are sorry, but your message was flagged as spam.  It will not be visible till an administrator has reviewed it."
                }
                return render(request, 'pastelsvg/message.html' , data) 
            return redirect(reverse('pastel-svg-request'))
    else:
        form = choose_form(request, RequestForm, RequestAnonymousForm)
    data = {
        "title": "Make Pastel SVG Icon Request",
        "form": form,
    }
    return render(request, 'pastelsvg/make_request.html' , data)

def request_icon(request, request_id):
    icon_request = get_object_or_404(IconRequest, is_spam=False, is_public=True, pk=request_id)
    if request.method == "POST":
        form = choose_form(request, IconRequestCommentForm, IconRequestCommentAnonymousForm, request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ip = get_client_ip(request)
            if request.user.is_authenticated():
                comment.poster = request.user
            comment.is_spam = check_askmet_spam(request, form)
            comment.request = icon_request
            comment.save()
            if comment.is_spam:
                data = {
                        "title": "Comment flagged as Spam",
                        "message": "We are sorry, but your message was flagged as spam.  It will not be visible till an administrator has reviewed it."
                }
                return render(request, 'pastelsvg/message.html' , data) 
    else:
        form = choose_form(request, IconRequestCommentForm, IconRequestCommentAnonymousForm)
    data = {
        "title": icon_request.title,
        "icon_request": icon_request,
        "form": form,
    }
    return render(request, 'pastelsvg/request.html' , data)

def request_icon_vote(request, request_id):
    if not request.session.get('pastel-svg-voted-%s' % request_id):
        request.session['pastel-svg-voted-%s' % request_id] = True
        icon_request = IconRequest.objects.filter(is_spam=False, is_public=True, closed=False, pk=request_id)
        if not icon_request:
            raise Http404
        icon_request.update(votes=models.F('votes') + 1)
    else:
        messages.add_message(request, messages.INFO, "You can't up vote an icon request multiple times.")
    return redirect(reverse('pastel-svg-request', kwargs={'request_id': request_id}))

def request_icon_vote_ajax(request, request_id):
    if not request.session.get('pastel-svg-voted-%s' % request_id):
        request.session['pastel-svg-voted-%s' % request_id] = True
        icon_request = IconRequest.objects.get(is_spam=False, is_public=True, closed=False, pk=request_id)
        if not icon_request:
            raise Http404
        icon_request.votes += 1
        icon_request.save()
        return HttpResponse(str(icon_request.votes))
    else:
        return HttpResponse("You can't up vote an icon request multiple times.")

@login_required
def request_icon_follow(request, request_id):
    icon_request = get_object_or_404(IconRequest, is_spam=False, is_public=True, pk=request_id)
    if not request.user.icon_request_subscriptions.filter(pk=request_id).exists():
        icon_request.subscriptions.add(request.user)
        messages.add_message(request, messages.SUCCESS, "You are now following this request.  You will receive an email when it is implemented.")
    else:
        messages.add_message(request, messages.INFO, "You are already following this request.")
    return redirect(reverse('pastel-svg-request', kwargs={'request_id': request_id}))

def request_icon_list(request, page=1):
    requests = IconRequest.objects.filter(is_spam=False, is_public=True).order_by('-votes')  
    paginator = Paginator(requests, 10)    
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        if page != 1:
            return redirect(requests[0].get_absolute_url(paginator.num_pages))
    data = {
        "title": "Pastel SVG Icon Requests",
        "page": page,
    }
    return render(request, 'pastelsvg/requests.html' , data)

def donate_thanks(request):
    data = {
        "title": "Thanks for your Donation"
    }
    return render(request, 'pastelsvg/donate_thanks.html' , data)

def donate(request):
    form = None
    if request.user.is_authenticated():
        try:
            donation = PastelSVGDonation.objects.get(user=request.user, validated=False)
        except PastelSVGDonation.DoesNotExist:
            invoice_id = 'pastel-svg-%s-%s' % (time.strftime("%y%m%d"), request.user.pk)
            donation = PastelSVGDonation(user=request.user, invoice_id=invoice_id)
            donation.save()
        paypal_dict = {
            "business": settings.PAYPAL_RECEIVER_EMAIL,
            "item_name": "Donation to Codefisher.org",
            "invoice": donation.invoice_id,
            "notify_url": "http://%s" % request.get_host() + reverse('paypal-ipn'),
            "return_url": "http://%s" % request.get_host() + reverse('pastel-svg-donate-thanks'),
            "cancel_return": "http://%s" % request.get_host() + reverse('pastel-svg-donate'),
        }
        # Create the instance.
        form = DonationPayPalPaymentsForm(initial=paypal_dict, button_type='donate')
    data = {
           "title": "Donate to Pastel SVG",
           "form": form,
    }
    return render(request, 'pastelsvg/donate.html' , data)

def get_download(download_id):
    try:
        group = DownloadGroup.objects.get(identifier=download_id)
    except DownloadGroup.DoesNotExist:
        return None
    try:
        download = Download.objects.get(pk=group.latest.pk)
    except Download.DoesNotExist:
        return None
    return group, download

def download(request):
    data = {}
    if not request.user.is_authenticated():
        pass
    elif not has_permission(request, 'pastelsvg', 'can_download_protected_files'):
        data = {
                "permission": False,
        }
    else:
        icon_group, icons = get_download('pastel.svg@codefisher.org')
        icon_group_large, icons_large = get_download('pastel.svg.large@codefisher.org')
        data = {
                "permission": True,
                "icon_group": icon_group,
                "icons": icons,
                "icon_group_large": icon_group_large,
                "icons_large": icons_large,
                "protected_files": ProtectedDownload.objects.filter(public=True).order_by('-release_date'),
        }
    data["title"] = "Pastel SVG Downloads"
    return render(request, 'pastelsvg/download.html' , data) 
    

def download_file(request, file, file_name):
    if request.user.is_authenticated() and has_permission(request, 'pastelsvg', 'can_download_protected_files'):
        download_file = get_object_or_404(ProtectedDownload, pk=file)
        responce =  HttpResponse('', content_type='')
        responce["X-Accel-Redirect"] =  download_file.file.url
        del responce['Content-Type']
        return responce
    else:
        raise Http404

def list_icons(request, page=1):
    if request.GET.get('name'):
        return redirect(reverse('pastel-svg-icon', kwargs={'file_name': request.GET.get('name')}))
    icon_list = Icon.objects.all().order_by('title')
    paginator = Paginator(icon_list, 30)
    try:
        icons = paginator.page(page)
    except (EmptyPage, InvalidPage):
        if page != 1:
            return redirect(icon_list[0].get_absolute_url(paginator.num_pages))  
    data = {
        "icon": icon_list[0],
        "title": "Pastel SVG Icons",
        "icons": icons,
    }
    return render(request, 'pastelsvg/list.html' , data)

def icon(request, file_name):
    icon_obj = get_object_or_404(Icon, file_name=file_name)
    searchqueryset = SearchQuerySet().auto_query(icon_obj.description).models(Icon)
    data = {
        "title": icon_obj.title,
        "icon": icon_obj,
        "searchqueryset": searchqueryset,
    }
    return render(request, 'pastelsvg/icon.html' , data)