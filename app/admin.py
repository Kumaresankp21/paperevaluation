from django.contrib import admin
from .models import Exam, ExamSubmission, EvaluationResult,APIKey


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('subject', 'exam_type', 'year', 'staff_name', 'created_at')
    list_filter = ('exam_type', 'year', 'staff_name')
    search_fields = ('subject', 'staff_name')


@admin.register(ExamSubmission)
class ExamSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'exam_type', 'year', 'staff_name', 'is_graded')
    list_filter = ('exam_type', 'year', 'is_graded')
    search_fields = ('student__username', 'subject', 'staff_name')


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ('submission', 'evaluated_by', 'total_score', 'max_score', 'created_at')
    search_fields = ('submission__student__username', 'submission__subject', 'evaluated_by__username')
    list_filter = ('created_at',)

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)