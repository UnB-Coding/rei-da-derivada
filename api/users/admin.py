from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django import forms
from .models import User


# class UserForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# class UserForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         for field in self.fields:
#             self.fields[field].required = False
#         self.fields['email'].required = True
#         for field in self.fields:
#             self.fields[field].required = False
#         self.fields['email'].required = True

#     class Meta:
#         model = User
#         fields = '__all__'
#     class Meta:
#         model = User
#         fields = '__all__'


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    # form = UserForm
    # form = UserForm

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)

    def event(self, user):
        events = []
        for event in user.events.all():
            events.append(event.name)
        return ' '.join(events)

    event.short_description = 'Events'

    def event(self, user):
        events = []
        for event in user.events.all():
            events.append(event.name)
        return ' '.join(events)

    event.short_description = 'Events'
    group.short_description = 'Groups'
    list_display = ['id', 'uuid', 'email', 'username',
                    'first_name', 'last_name', 'is_active', 'group', 'event']
    search_fields = ['email']
    filter_horizontal = ('groups', 'events')
    filter_horizontal = ('groups', 'events')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'groups', 'events'),
            'fields': ('email', 'username', 'password1', 'password2', 'first_name', 'last_name', 'is_active', 'groups', 'events')}
         ),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',
         'is_staff', 'is_superuser', 'groups')}),
        ('Events', {'fields': ('events',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active',
         'is_staff', 'is_superuser', 'groups')}),
        ('Events', {'fields': ('events',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
