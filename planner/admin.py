from django.contrib import admin
from .models import Quote

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ("text", "mood", "active")
    list_filter = ("active", "mood")
    search_fields = ("text",)

