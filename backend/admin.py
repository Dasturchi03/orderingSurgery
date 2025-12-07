from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.contrib.auth.models import Group


admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Branches', {'fields': ('branches', )})
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )

    list_display = ('username', 'first_name', 'last_name', 'role',)
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)

    filter_horizontal = ['branches']


@admin.register(Surgeon)
class SurgeonAdmin(admin.ModelAdmin):
    list_display = [
        'full_name'
    ]


class UserInline(admin.TabularInline):
    model = CustomUser.branches.through


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = [
        'branch_number',
        'name',
        'page_number'
    ]
    inlines = [UserInline]


# admin.site.register(SurgeryName)
# admin.site.register(SurgeryType)

@admin.register(Surgery)
class SurgeryAdmin(admin.ModelAdmin):
    list_display = [
        'seq_number',
        'branch',
        'surgery_name'
    ]


@admin.register(SurgeryDay)
class SurgeryDayAdmin(admin.ModelAdmin):
    fields = ['date']
