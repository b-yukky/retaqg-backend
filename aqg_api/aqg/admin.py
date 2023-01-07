from django.contrib import admin
from .models import *
# Register your models here.

@admin.action(description='Mark selected questions as to evaluate')
def make_toevaluate(modeladmin, request, queryset):
    queryset.update(status='EV')
    
@admin.action(description='Mark selected questions as test')
def make_totest(modeladmin, request, queryset):
    queryset.update(status='TE')

@admin.action(description='Mark selected questions as to evaluate')
def make_paragraph_toevaluate(modeladmin, request, queryset):
    for paragraph in queryset:
        paragraph.questions.update(status='EV')
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'status']
    actions = [make_toevaluate, make_totest]

class ParagraphAdmin(admin.ModelAdmin):
    list_display = ['text', 'topic', 'length']
    actions = [make_paragraph_toevaluate]  
    
admin.site.register(Paragraph, ParagraphAdmin)
admin.site.register(Model)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Evaluation)
admin.site.register(Distractor)
admin.site.register(Profile)
