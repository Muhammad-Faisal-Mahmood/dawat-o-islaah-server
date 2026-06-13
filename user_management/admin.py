from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # ✅ Added latitude and longitude to the list view columns
    list_display = ('email', 'first_name', 'last_name', 'role', 'latitude', 'longitude', 'is_staff', 'is_active', 'date_joined')
    
    # Fields to filter by in the right sidebar
    list_filter = ('role', 'is_staff', 'is_active', 'date_joined')
    
    # Fields to search by in the search bar
    search_fields = ('email', 'first_name', 'last_name')
    
    # Fields to display in the detail/edit view, grouped into sections
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),

        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        
        ('Preferences', {
            'fields': ('receive_daily_email',)
        }),

        # ✅ NEW: Location Info section
        ('Location Info', {
            'fields': ('latitude', 'longitude')
        }),
    )
    
    # Fields to display in the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    
    # Order users by date joined in descending order
    ordering = ('-date_joined',)
    
    # Add custom actions
    actions = ['make_admin', 'make_mufti', 'make_basicuser']

    @admin.action(description='Mark selected users as Admin')
    def make_admin(self, request, queryset):
        queryset.update(role='admin')

    @admin.action(description='Mark selected users as Mufti')
    def make_mufti(self, request, queryset):
        queryset.update(role='mufti')

    @admin.action(description='Mark selected users as Basic User')
    def make_basicuser(self, request, queryset):
        queryset.update(role='basicuser')

# ✅ Safe registration to avoid "AlreadyRegistered" errors
if admin.site.is_registered(User):
    admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
