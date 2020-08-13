from django.contrib import admin
from .models import Except, Verb

# Register your models here.


class VerbInline(admin.StackedInline):
    model = Except.verbs.through
    readonly_fields = ['verb']
    extra = 0


@admin.register(Except)
class ExceptAdmin(admin.ModelAdmin):
    model = Except
    inlines = [VerbInline]
    exclude = ['verbs']
