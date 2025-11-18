from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import (
    UserProfile, SavedProposal, ProposalType, ProposalTemplate,
    ProposalSection, ProposalCollaborator, ProposalComment, ProposalAnalytics
)


# Inline profile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'first_name', 'last_name', 'university', 'department', 'position',
        'orcid', 'bio', 'avatar', 'total_proposals_generated',
        'total_proposals_saved', 'total_words_generated', 'created_at', 'updated_at'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'total_proposals_generated',
        'total_proposals_saved', 'total_words_generated'
    )


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


# UserProfile admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_full_name', 'university', 'position',
        'total_proposals_generated', 'created_at'
    )
    list_filter = ('university', 'position', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name', 'university', 'department', 'orcid')
    readonly_fields = (
        'created_at', 'updated_at', 'total_proposals_generated',
        'total_proposals_saved', 'total_words_generated'
    )

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'first_name', 'last_name', 'university', 'department', 'position')
        }),
        ('Academic Profile', {
            'fields': ('orcid', 'bio', 'avatar')
        }),
        ('Statistics', {
            'fields': ('total_proposals_generated', 'total_proposals_saved', 'total_words_generated'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


# ProposalType admin
class ProposalTemplateInline(admin.TabularInline):
    model = ProposalTemplate
    extra = 1
    fields = ('section_name', 'section_order', 'is_required', 'min_words', 'max_words')
    ordering = ['section_order']


@admin.register(ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'is_active', 'min_pages', 'max_pages',
        'template_count', 'created_at'
    )
    list_filter = ('is_active', 'code', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProposalTemplateInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'logo', 'is_active')
        }),
        ('Requirements', {
            'fields': ('min_pages', 'max_pages', 'required_sections', 'optional_sections')
        }),
        ('Guidelines', {
            'fields': ('guidelines_url', 'submission_deadline')
        }),
        ('Styling', {
            'fields': ('template_style',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def template_count(self, obj):
        return obj.templates.count()
    template_count.short_description = 'Templates'


# ProposalTemplate admin
@admin.register(ProposalTemplate)
class ProposalTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'section_name', 'proposal_type', 'section_order', 'is_required',
        'min_words', 'max_words'
    )
    list_filter = ('proposal_type', 'is_required')
    search_fields = ('section_name', 'description', 'proposal_type__name')
    ordering = ['proposal_type', 'section_order']

    fieldsets = (
        ('Basic Information', {
            'fields': ('proposal_type', 'section_name', 'section_order', 'is_required')
        }),
        ('Specifications', {
            'fields': ('min_words', 'max_words', 'description')
        }),
        ('Content Generation', {
            'fields': ('prompt_template', 'example_content'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# SavedProposal admin
class ProposalSectionInline(admin.TabularInline):
    model = ProposalSection
    extra = 0
    fields = ('section_name', 'section_order', 'word_count', 'is_complete')
    readonly_fields = ('word_count',)
    ordering = ['section_order']


@admin.register(SavedProposal)
class SavedProposalAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'user', 'proposal_type', 'status', 'version',
        'word_count', 'page_count', 'citation_count', 'created_at'
    )
    list_filter = ('status', 'proposal_type', 'is_latest', 'created_at')
    search_fields = ('title', 'keywords', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'word_count', 'page_count', 'citation_count')
    date_hierarchy = 'created_at'
    inlines = [ProposalSectionInline]

    fieldsets = (
        ('Proposal Information', {
            'fields': ('user', 'proposal_type', 'title', 'keywords', 'description', 'status', 'tags')
        }),
        ('Versioning', {
            'fields': ('version', 'is_latest', 'parent_proposal')
        }),
        ('Content', {
            'fields': ('content', 'content_json'),
            'classes': ('collapse',)
        }),
        ('RAG Data', {
            'fields': ('retrieved_papers', 'citations_data'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('word_count', 'page_count', 'citation_count')
        }),
        ('Sharing', {
            'fields': ('is_public', 'share_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'user__profile', 'proposal_type')


# ProposalSection admin
@admin.register(ProposalSection)
class ProposalSectionAdmin(admin.ModelAdmin):
    list_display = (
        'section_name', 'get_proposal_title', 'section_order',
        'word_count', 'citation_count', 'is_complete', 'needs_review'
    )
    list_filter = ('is_complete', 'needs_review', 'created_at')
    search_fields = ('section_name', 'proposal__title', 'content')
    ordering = ['proposal', 'section_order']
    readonly_fields = ('created_at', 'updated_at', 'word_count', 'citation_count')

    def get_proposal_title(self, obj):
        return obj.proposal.title
    get_proposal_title.short_description = 'Proposal'


# ProposalCollaborator admin
@admin.register(ProposalCollaborator)
class ProposalCollaboratorAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_proposal_title', 'role', 'invited_by', 'invited_at', 'accepted_at'
    )
    list_filter = ('role', 'invited_at', 'accepted_at')
    search_fields = ('user__username', 'proposal__title', 'invited_by__username')
    readonly_fields = ('invited_at',)
    date_hierarchy = 'invited_at'

    def get_proposal_title(self, obj):
        return obj.proposal.title
    get_proposal_title.short_description = 'Proposal'


# ProposalComment admin
@admin.register(ProposalComment)
class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'get_proposal_title', 'get_section_name',
        'is_resolved', 'created_at'
    )
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('content', 'user__username', 'proposal__title')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def get_proposal_title(self, obj):
        return obj.proposal.title
    get_proposal_title.short_description = 'Proposal'

    def get_section_name(self, obj):
        return obj.section.section_name if obj.section else 'General'
    get_section_name.short_description = 'Section'


# ProposalAnalytics admin
@admin.register(ProposalAnalytics)
class ProposalAnalyticsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'action', 'get_proposal_title', 'execution_time', 'created_at'
    )
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'proposal__title', 'action')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def get_proposal_title(self, obj):
        return obj.proposal.title if obj.proposal else 'N/A'
    get_proposal_title.short_description = 'Proposal'


# Customize admin site header
admin.site.site_header = 'Grant Proposal Generator Admin'
admin.site.site_title = 'GPG Admin Portal'
admin.site.index_title = 'Welcome to Grant Proposal Generator Administration'