from django.contrib import admin
from .models import Team

# Register your models here.

#admin.site.register(Teams)

class AdminTeams(admin.ModelAdmin):
    list_display = ('first_name', 'last_name','designation',)

admin.site.register(Team, AdminTeams)