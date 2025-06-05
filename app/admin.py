from django.contrib import admin
from .models import Script, PostURL, ClaimURL

class ScriptAdmin(admin.ModelAdmin):
    list_display = ('user', 'textarea1', 'textarea2', 'textarea3', 'textarea4', 'coin', 'created_at')

class PostURLAdmin(admin.ModelAdmin):
    list_display = ('user', 'post_char', 'claim_char','token')

class ClaimURLAdmin(admin.ModelAdmin):
    list_display = ('claim_char', 'user')

admin.site.register(Script, ScriptAdmin)
admin.site.register(PostURL, PostURLAdmin)
admin.site.register(ClaimURL, ClaimURLAdmin)
