from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, SavedProposal

# Inline profile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('first_name', 'last_name', 'university', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

# Extend User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'get_full_name', 'get_university', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'profile__first_name', 'profile__last_name', 'profile__university')
    
    def get_full_name(self, obj):
        try:
            return f"{obj.profile.first_name} {obj.profile.last_name}"
        except UserProfile.DoesNotExist:
            return "No Profile"
    get_full_name.short_description = 'Full Name'

    def get_university(self, obj):
        try:
            return obj.profile.university
        except UserProfile.DoesNotExist:
            return "No Profile"
    get_university.short_description = 'University'

# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# UserProfile admin (optional, since it's inline with User)
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'university', 'created_at')
    list_filter = ('university', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name', 'university')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'last_name', 'university')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# SavedProposal admin
@admin.register(SavedProposal)
class SavedProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'word_count', 'citation_count', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'keywords', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'word_count', 'citation_count')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Proposal Information', {
            'fields': ('user', 'title', 'keywords', 'description')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('word_count', 'citation_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'user__profile')

# Customize admin site header
admin.site.site_header = 'Grant Proposal Generator Admin'
admin.site.site_title = 'GPG Admin Portal'
admin.site.index_title = 'Welcome to Grant Proposal Generator Administration'