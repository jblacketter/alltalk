from django.contrib import admin
from .models import Dream, DreamTag, DreamImage


class DreamImageInline(admin.TabularInline):
    """Inline admin for dream images."""
    model = DreamImage
    extra = 1
    fields = ['image', 'image_url', 'caption', 'order', 'thumbnail']
    readonly_fields = ['thumbnail']
    ordering = ['order']


@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'dream_date', 'privacy_level', 'lucidity_level', 'created_at']
    list_filter = ['privacy_level', 'dream_date', 'lucidity_level', 'created_at']
    search_fields = ['title', 'description', 'transcription', 'mood']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'dream_date'
    inlines = [DreamImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'dream_date')
        }),
        ('Content', {
            'fields': ('description', 'voice_recording', 'transcription')
        }),
        ('Metadata', {
            'fields': ('mood', 'lucidity_level', 'privacy_level')
        }),
        ('AI Analysis', {
            'fields': ('themes', 'symbols', 'entities'),
            'classes': ('collapse',)
        }),
        ('Sharing', {
            'fields': ('shared_with_users', 'shared_with_groups'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    filter_horizontal = ['shared_with_users', 'shared_with_groups']


@admin.register(DreamTag)
class DreamTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'dream_count', 'created_at']
    search_fields = ['name']
    
    def dream_count(self, obj):
        return obj.dreams.count()
    dream_count.short_description = 'Dreams'


@admin.register(DreamImage)
class DreamImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'dream', 'caption', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['dream__title', 'caption']
    readonly_fields = ['thumbnail', 'created_at']
    ordering = ['dream', 'order']
    
    fieldsets = (
        ('Dream', {
            'fields': ('dream',)
        }),
        ('Image', {
            'fields': ('image', 'image_url', 'thumbnail')
        }),
        ('Details', {
            'fields': ('caption', 'order', 'created_at')
        })
    )
