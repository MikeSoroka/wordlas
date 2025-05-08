from django.contrib import admin
from .models import Word

class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'category', 'difficulty_level', 'active', 'created_at')
    list_filter = ('category', 'difficulty_level', 'active', 'created_at')
    search_fields = ('word',)
    ordering = ('word',)
    date_hierarchy = 'created_at'
    list_editable = ('category', 'difficulty_level', 'active')
    list_per_page = 25
    
    fieldsets = (
        ('Word Information', {
            'fields': ('word', 'category', 'difficulty_level')
        }),
        ('Status', {
            'fields': ('active',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_inactive']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(active=True)
        self.message_user(request, f'{updated} words have been marked as active.')
    mark_as_active.short_description = "Mark selected words as active"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(active=False)
        self.message_user(request, f'{updated} words have been marked as inactive.')
    mark_as_inactive.short_description = "Mark selected words as inactive"

# Register the model with the custom admin class
admin.site.register(Word, WordAdmin)
