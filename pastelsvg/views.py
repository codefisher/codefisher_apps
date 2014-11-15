import time
from django.shortcuts import render, get_object_or_404, redirect
from codefisher_apps.pastelsvg.models import Icon, PastelSVGDonation, ProtectedDownload, IconRequest, IconRequestComment, UseExample
from haystack.query import SearchQuerySet
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.http import Http404, HttpResponse
from djangopress.donate.views import DonationPayPalPaymentsForm
from django.core.urlresolvers import reverse
from django.conf import settings
from djangopress.core.util import has_permission, get_client_ip, choose_form
from codefisher_apps.downloads.models import Download, DownloadGroup
from django import forms
from django.contrib import messages
# we use the same fields so this works
from djangopress.forum.views import check_askmet_spam

from upvotes.views import MakeRequest, RequestList, RequestView, RequestVote, RequestFollow
from upvotes.forms import get_request_form, get_anon_request_form, get_request_comment_form, get_anon_request_comment_form

IconRequestForm = get_request_form(IconRequest, ('concept_icon', ))
IconRequestAnonymousForm = get_anon_request_form(IconRequest, ('concept_icon', ))
IconRequestCommentForm = get_request_comment_form(IconRequestComment)
IconRequestCommentAnonymousForm = get_anon_request_comment_form(IconRequestComment)

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
      
class UseExampleForm(forms.ModelForm):
    class Meta(object):
        fields = ("title", "url", "description")
        model = UseExample
       
class UseExampleAnonymousForm(UseExampleForm):
    class Meta(object):
        fields = ("title", "poster_name", "poster_email", "url", "description")
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

class MakeIconRequet(MakeRequest):
    template = 'pastelsvg/request/make.html'
    title = "Make Pastel SVG Icon Request"
    request_url = 'pastel-svg-request'
    spam_url = 'pastel-svg-request-spam'
    request_form = IconRequestForm
    request_anonymous_form = IconRequestAnonymousForm
    
class IconRequestView(RequestView):
    template = 'pastelsvg/request/request.html'
    request_class = IconRequest
    spam_url = 'pastel-svg-request-comment-spam'
    request_url = 'pastel-svg-request'
    comment_form = IconRequestCommentForm
    comment_anonymous_form = IconRequestCommentAnonymousForm
   
class IconRequestVote(RequestVote):
    request_class = IconRequest
    session_id = 'pastel-svg-voted-%s'
    request_url = 'pastel-svg-request'
    duplicate_vote_message = "You can not up vote an icon request multiple times."

class IconRequestFollow(RequestFollow):
    request_class = IconRequest
    request_url = 'pastel-svg-request'

    def get_subscriptions(self, request):
        return request.user.icon_request_subscriptions

class RequestIconList(RequestList):
    template = 'pastelsvg/request/index.html'
    title = "Pastel SVG Icon Requests"
    request_class = IconRequest
    
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