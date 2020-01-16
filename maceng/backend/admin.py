from django.contrib import admin
from .models import User, Score

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'team', 'email')
    readonly_fields = ('username', 'team', 'email')

class ScoreAdmin(admin.ModelAdmin):
	list_display = ('score', 'user', 'datetime')
	readonly_fields = ('score', 'user', 'datetime')

admin.site.register(User, UserAdmin)
admin.site.register(Score, ScoreAdmin)