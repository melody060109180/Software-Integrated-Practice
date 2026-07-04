from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Address


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '用户信息'


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, AddressInline)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'phone', 'province', 'city', 'district', 'is_default']
    list_filter = ['is_default']
    search_fields = ['user__username', 'name', 'phone']
