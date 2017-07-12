from django.views.generic import View
from djangopress.core.util import choose_form, get_client_ip
from djangopress.forum.views import check_askmet_spam
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

class MakeRequest(View):
    template = None
    title = None
    request_url = None
    request_form = None
    request_anonymous_form = None
    spam_url = None
    
    def get(self, request):
        return render(request, self.template , {
            "title": self.title,
            "form": choose_form(request, self.request_form, self.request_anonymous_form),
        })
        
    def post(self, request):
        form = choose_form(request, self.request_form, self.request_anonymous_form, request.POST)
        if form.is_valid():
            icon_request = form.save(commit=False)
            icon_request.ip = get_client_ip(request)
            if request.user.is_authenticated():
                icon_request.poster = request.user
            icon_request.is_spam = check_askmet_spam(request, form)
            icon_request.save()
            if icon_request.is_spam:
                return redirect(reverse(self.spam_url)) 
            return redirect(reverse(self.request_url))
        return render(request, self.template , {
            "title": self.title,
            "form": form,
        })
 
def request_spam(request):    
    return render(request, 'upvotes/message.html' , data = {
            "title": "Request flagged as Spam",
            "message": "We are sorry, but your message was flagged as spam.  It will not be visible till an administrator has reviewed it."
    })   

        
class RequestList(View):
    template = None
    title = None
    request_class = None
    
    def post(self, request, page=1):
        return self.get(request, page=page)
    
    def get(self, request, page=1):
        requests = self.request_class.objects.filter(is_spam=False, is_public=True).order_by('-votes', '-posted')  
        paginator = Paginator(requests, 10)    
        try:
            page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            if page != 1:
                return redirect(requests[0].get_absolute_url(paginator.num_pages))
        return render(request, self.template , {
            "title": self.title,
            "page": page,
        })

class RequestView(View):
    template = None
    request_class = None
    spam_url = None
    request_url = None
    comment_form = None
    comment_anonymous_form = None
    
    def post(self, request, request_id):
        upvote_request = get_object_or_404(self.request_class, is_spam=False, is_public=True, pk=request_id)
        form = choose_form(request, self.comment_form, self.comment_anonymous_form, request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ip = get_client_ip(request)
            if request.user.is_authenticated():
                comment.poster = request.user
            comment.is_spam = check_askmet_spam(request, form)
            comment.request = upvote_request
            comment.save()
            if comment.is_spam:
                return redirect(reverse(self.spam_url)) 
            return redirect(reverse(self.request_url, kwargs={'request_id': request_id})) 
        return self.display(request, upvote_request, form)
    
    def get(self, request, request_id):
        upvote_request = get_object_or_404(self.request_class, is_spam=False, is_public=True, pk=request_id)
        form = choose_form(request, self.comment_form, self.comment_anonymous_form)
        return self.display(request, upvote_request, form)
    
    def display(self, request, upvote_request, form):
        return render(request, self.template, {
            "title": upvote_request.title,
            "upvote_request": upvote_request,
            "form": form,
        })
    
def comment_spam(request):
    return render(request, 'upvotes/message.html' , {
            "title": "Comment flagged as Spam",
            "message": "We are sorry, but your comment was flagged as spam.  It will not be visible till an administrator has reviewed it."
    }) 
    
class RequestVote(View):
    request_class = None
    session_id = None
    request_url = None
    duplicate_vote_message = "You can not up vote a request multiple times."
    error_message = "This request could not be up voted."
    
    def post(self, request):
        request_id = request.POST.get('request')
        if request.POST.get('type') == 'ajax':
            if not request.session.get(self.session_id % request_id):
                request.session[self.session_id % request_id] = True
                upvote_request = self.request_class.objects.get(is_spam=False, is_public=True, closed=False, pk=request_id)
                if not upvote_request:
                    raise Http404
                upvote_request.votes += 1
                upvote_request.save()
                return HttpResponse(str(upvote_request.votes))
            else:
                return HttpResponse(self.duplicate_vote_message)
        else:
            if not request.session.get(self.session_id % request_id):
                request.session[self.session_id % request_id] = True
                upvote_request = self.request_class.objects.filter(is_spam=False, is_public=True, closed=False, pk=request_id)
                if not upvote_request:
                    messages.add_message(request, messages.ERROR, self.error_message)
                    return redirect(reverse(self.request_url, kwargs={'request_id': request_id}))
                upvote_request.update(votes=models.F('votes') + 1)
            else:
                messages.add_message(request, messages.INFO, self.duplicate_vote_message)
            return redirect(reverse(self.request_url, kwargs={'request_id': request_id}))
         
class RequestFollow(View):
    request_class = None
    request_url = None

    @method_decorator(login_required)
    def post(self, request):
        request_id = request.POST.get('request')
        upvote_request = get_object_or_404(self.request_class, is_spam=False, is_public=True, pk=request_id)
        if not self.get_subscriptions(request).filter(pk=request_id).exists():
            upvote_request.subscriptions.add(request.user)
            messages.add_message(request, messages.SUCCESS, "You are now following this request.  You will receive an email when it is implemented.")
        else:
            messages.add_message(request, messages.INFO, "You are already following this request.")
        return redirect(reverse(self.request_url, kwargs={'request_id': request_id}))
    
    def get(self, request):
        return redirect(reverse(self.request_url))
    
    def get_subscriptions(self, request):
        raise NotImplementedError