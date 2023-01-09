from django.contrib import admin
from .models import *
# Register your models here.

@admin.action(description='Mark selected questions as to evaluate')
def make_toevaluate(modeladmin, request, queryset):
    queryset.update(status='EV')
    
@admin.action(description='Mark selected questions as test')
def make_totest(modeladmin, request, queryset):
    queryset.update(status='TE')

@admin.action(description='Mark selected paragraphs as to evaluate')
def make_paragraph_toevaluate(modeladmin, request, queryset):
    for paragraph in queryset:
        paragraph.questions.update(status='EV')
        
@admin.action(description='Mark selected paragraphs to dataset Wikipedia')
def paragraph2wikipedia(modeladmin, request, queryset):
    queryset.update(dataset=Dataset.objects.get(name='Wikipedia'))

@admin.action(description='Mark selected paragraphs to dataset OpenLearn')
def paragraph2openlearn(modeladmin, request, queryset):
    queryset.update(dataset=Dataset.objects.get(name='OpenLearn'))

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'status']
    actions = [make_toevaluate, make_totest]

class ParagraphAdmin(admin.ModelAdmin):
    list_display = ['text', 'topic', 'dataset', 'length']
    actions = [make_paragraph_toevaluate, paragraph2wikipedia, paragraph2openlearn]  
    
admin.site.register(Paragraph, ParagraphAdmin)
admin.site.register(Model)
admin.site.register(Dataset)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Evaluation)
admin.site.register(Distractor)
admin.site.register(Profile)
admin.site.register(ExperimentSetting)
