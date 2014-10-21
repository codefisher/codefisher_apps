from django.contrib import admin

class RequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'posted', 'votes', 'is_spam', 'is_public', 'closed')

class RequestCommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'posted', 'is_spam', 'is_public')
    