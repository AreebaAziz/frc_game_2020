import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import User, Score

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

class UserAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('username', 'team', 'email')
    readonly_fields = ('username', 'team', 'email')
    actions = ['export_as_csv']

class ScoreAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('score', 'user', 'get_user_email', 'get_user_team', 'datetime')
    list_filter = ('datetime', )
    readonly_fields = ('score', 'user', 'datetime')
    actions = ["export_as_csv"]

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = "User Email"
    get_user_email.admin_order_field = "user__email"

    def get_user_team(self, obj):
        return obj.user.team
    get_user_team.short_description = "User Team"
    get_user_team.admin_order_field = "user__team"

admin.site.register(User, UserAdmin)
admin.site.register(Score, ScoreAdmin)
