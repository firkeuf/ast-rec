from django.contrib import admin
from ast_rec.models import Cdr, ChannelList

class CdrUvitaAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['src']}),
        ('Date information', {'fields': ['dst'], 'classes': ['collapse']}),
    ]
    list_display = ('src', 'dst', 'calldate', 'billsec')
    list_filter = ['src']
    search_fields = ['calldate']

class Channel_listAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Cdr, CdrUvitaAdmin)
admin.site.register(ChannelList, Channel_listAdmin)
