from django.contrib import admin
from django import forms
from .models import User


class UserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].required = False
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserForm

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)

    group.short_description = 'Groups'
    list_display = ['uuid', 'email', 'username',
                    'first_name', 'last_name', 'is_active', 'group']
    search_fields = ['email']
    fields = [('first_name', 'last_name'), 'email', 'username', 'is_active', 'is_staff',
              'is_superuser', 'groups', 'user_permissions']
