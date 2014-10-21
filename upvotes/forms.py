from django import forms

def get_request_form(request_model, extra_fields):
    class RequestForm(forms.ModelForm):
        class Meta(object):
            fields = ('title', 'message',) + extra_fields
            model = request_model
    return RequestForm

def get_anon_request_form(request_model, extra_fields):
    class RequestAnonymousForm(forms.ModelForm):
        class Meta(object):
            fields = ('title', 'poster_name', 'poster_email', 'message',) + extra_fields
            model = request_model
            
        def __init__(self, *args, **kwargs):
            super(RequestAnonymousForm, self).__init__(*args, **kwargs)
            self.fields['poster_name'].required = True
            self.fields['poster_email'].required = True
    return RequestAnonymousForm

def get_request_comment_form(comment_model):
    class RequestCommentForm(forms.ModelForm):
        class Meta(object):
            fields = ("message", )
            model = comment_model
        
        def __init__(self, *args, **kwargs):
            super(RequestCommentForm, self).__init__(*args, **kwargs)
            self.fields['message'].widget = forms.Textarea(attrs={'rows':3})
    return RequestCommentForm
 
def get_anon_request_comment_form(comment_model):       
    class RequestCommentAnonymousForm(forms.ModelForm):
        class Meta(object):
            fields = ("poster_name", "poster_email", "message")
            model = comment_model
        
        def __init__(self, *args, **kwargs):
            super(RequestCommentAnonymousForm, self).__init__(*args, **kwargs)
            self.fields['message'].widget = forms.Textarea(attrs={'rows':3})
            self.fields['poster_name'].required = True
            self.fields['poster_email'].required = True
    return RequestCommentAnonymousForm