from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class UserProfile(models.Model):
    """Extended user profile with academic information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    university = models.CharField(max_length=200)
    department = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)  # Professor, Researcher, PhD Student, etc.
    orcid = models.CharField(max_length=19, blank=True, null=True, help_text="ORCID iD")
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Analytics
    total_proposals_generated = models.IntegerField(default=0)
    total_proposals_saved = models.IntegerField(default=0)
    total_words_generated = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.university}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'


# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class ProposalType(models.Model):
    """Funding body types (Horizon Europe, NSF, NIH, etc.)"""
    FUNDING_BODY_CHOICES = [
        ('horizon_europe', 'Horizon Europe'),
        ('europol', 'Europol'),
        ('nsf', 'National Science Foundation (NSF)'),
        ('nih', 'National Institutes of Health (NIH)'),
        ('erc', 'European Research Council (ERC)'),
        ('marie_curie', 'Marie Skłodowska-Curie Actions'),
        ('wellcome_trust', 'Wellcome Trust'),
        ('gates_foundation', 'Gates Foundation'),
        ('darpa', 'DARPA'),
        ('uk_research', 'UK Research and Innovation'),
        ('custom', 'Custom Template'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, choices=FUNDING_BODY_CHOICES)
    description = models.TextField()
    logo = models.ImageField(upload_to='proposal_types/', blank=True, null=True)

    # Requirements
    min_pages = models.IntegerField(default=10)
    max_pages = models.IntegerField(default=100)
    required_sections = models.JSONField(default=list)  # List of required section names
    optional_sections = models.JSONField(default=list)

    # Guidelines
    guidelines_url = models.URLField(blank=True, null=True)
    submission_deadline = models.DateField(blank=True, null=True)

    # Styling
    template_style = models.JSONField(default=dict)  # Font, margins, spacing requirements

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'proposal_types'
        verbose_name = 'Proposal Type'
        verbose_name_plural = 'Proposal Types'
        ordering = ['name']


class ProposalTemplate(models.Model):
    """Section templates for each proposal type"""
    proposal_type = models.ForeignKey(ProposalType, on_delete=models.CASCADE, related_name='templates')
    section_name = models.CharField(max_length=200)
    section_order = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)

    # Section specifications
    min_words = models.IntegerField(default=0)
    max_words = models.IntegerField(default=0)
    description = models.TextField()
    prompt_template = models.TextField(help_text="Template for AI generation")

    # Example content
    example_content = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.proposal_type.name} - {self.section_name}"

    class Meta:
        db_table = 'proposal_templates'
        verbose_name = 'Proposal Template'
        verbose_name_plural = 'Proposal Templates'
        ordering = ['proposal_type', 'section_order']
        unique_together = ['proposal_type', 'section_name']


class SavedProposal(models.Model):
    """Enhanced saved proposal with versioning and status tracking"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('review', 'Under Review'),
        ('final', 'Final'),
        ('submitted', 'Submitted'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    proposal_type = models.ForeignKey(ProposalType, on_delete=models.SET_NULL, null=True, blank=True)

    # Basic Information
    title = models.CharField(max_length=500)
    keywords = models.TextField(blank=True, null=True)
    description = models.TextField()

    # Content
    content = models.TextField()  # Full proposal text
    content_json = models.JSONField(default=dict, blank=True)  # Structured content by section

    # RAG Data
    retrieved_papers = models.JSONField(default=list, blank=True)  # Papers retrieved by RAG
    citations_data = models.JSONField(default=dict, blank=True)  # Citation metadata

    # Metadata
    word_count = models.IntegerField(default=0)
    page_count = models.FloatField(default=0)
    citation_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # Version tracking
    version = models.IntegerField(default=1)
    is_latest = models.BooleanField(default=True)
    parent_proposal = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='versions')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # Tags
    tags = models.JSONField(default=list, blank=True)

    # Sharing
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.title} - {self.user.username} (v{self.version})"

    def save(self, *args, **kwargs):
        # Calculate metrics
        self.word_count = len(self.content.split())
        self.page_count = self.word_count / 500  # Approximate 500 words per page

        super().save(*args, **kwargs)

    def create_version(self):
        """Create a new version of this proposal"""
        new_version = SavedProposal.objects.create(
            user=self.user,
            proposal_type=self.proposal_type,
            title=self.title,
            keywords=self.keywords,
            description=self.description,
            content=self.content,
            content_json=self.content_json,
            retrieved_papers=self.retrieved_papers,
            citations_data=self.citations_data,
            status=self.status,
            version=self.version + 1,
            parent_proposal=self.parent_proposal or self,
            tags=self.tags,
        )

        # Mark previous versions as not latest
        SavedProposal.objects.filter(
            parent_proposal=self.parent_proposal or self
        ).update(is_latest=False)

        return new_version

    class Meta:
        db_table = 'saved_proposals'
        ordering = ['-created_at']
        verbose_name = 'Saved Proposal'
        verbose_name_plural = 'Saved Proposals'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['proposal_type']),
        ]


class ProposalSection(models.Model):
    """Individual sections of a proposal"""
    proposal = models.ForeignKey(SavedProposal, on_delete=models.CASCADE, related_name='sections')
    template = models.ForeignKey(ProposalTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    section_name = models.CharField(max_length=200)
    section_order = models.IntegerField(default=0)
    content = models.TextField()

    # Metadata
    word_count = models.IntegerField(default=0)
    citation_count = models.IntegerField(default=0)

    # Status
    is_complete = models.BooleanField(default=False)
    needs_review = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.proposal.title} - {self.section_name}"

    def save(self, *args, **kwargs):
        self.word_count = len(self.content.split())
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'proposal_sections'
        ordering = ['proposal', 'section_order']
        unique_together = ['proposal', 'section_name']


class ProposalCollaborator(models.Model):
    """Collaborators on a proposal"""
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('reviewer', 'Reviewer'),
        ('viewer', 'Viewer'),
    ]

    proposal = models.ForeignKey(SavedProposal, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaborations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')

    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invitations_sent')
    invited_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.proposal.title} ({self.role})"

    class Meta:
        db_table = 'proposal_collaborators'
        unique_together = ['proposal', 'user']
        verbose_name = 'Proposal Collaborator'
        verbose_name_plural = 'Proposal Collaborators'


class ProposalComment(models.Model):
    """Comments and feedback on proposals"""
    proposal = models.ForeignKey(SavedProposal, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposal_comments')
    section = models.ForeignKey(ProposalSection, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')

    content = models.TextField()
    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.proposal.title}"

    class Meta:
        db_table = 'proposal_comments'
        ordering = ['-created_at']


class ProposalAnalytics(models.Model):
    """Track user activity and proposal generation analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    proposal = models.ForeignKey(SavedProposal, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')

    ACTION_CHOICES = [
        ('generate', 'Generate Proposal'),
        ('enhance', 'Enhance Proposal'),
        ('save', 'Save Proposal'),
        ('download', 'Download Proposal'),
        ('delete', 'Delete Proposal'),
        ('share', 'Share Proposal'),
        ('view', 'View Proposal'),
    ]

    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)  # Additional data about the action

    # Performance metrics
    execution_time = models.FloatField(null=True, blank=True)  # Time in seconds

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.created_at}"

    class Meta:
        db_table = 'proposal_analytics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action']),
        ]