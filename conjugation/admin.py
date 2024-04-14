from django.contrib import admin
from .models import Except, Verb, Regle, VerbSEO


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


@admin.register(Verb)
class VerbAdmin(admin.ModelAdmin):
    search_fields = ['infinitive', 'infinitive_no_accents']
    list_filter = [
        'group_no',
        'aspirate_h',
        'reflexive_only',
        'can_be_pronoun',
        'is_defective',
        'masculin_only',
        'has_passive',
        'has_second_form',
        'has_s_en',
        's_en',
        'can_passive',
        'can_feminin',
        'can_reflexive',
        'is_second_form',
        'is_frequent',
        'is_transitive',
        'is_intransitive',
        'is_pronominal',
        'belgium',
        'africa',
        'conjugated_with_avoir',
        'conjugated_with_etre',
        'is_impersonal',
        'book',
        'is_rare',
        'is_archaique',
        'is_slang',
        'is_etre_verb',
    ]


@admin.register(Regle)
class RegleAdmin(admin.ModelAdmin):
    search_fields = ['verb__infinitive', 'verb__infinitive_no_accents']


@admin.register(VerbSEO)
class VerbSEOAdmin(admin.ModelAdmin):
    list_display = ['verb', 'title', 'description']
    raw_id_fields = ['verb']