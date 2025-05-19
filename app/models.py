from django.db import models
from django.contrib.auth.models import User


class Exam(models.Model):
    YEAR_CHOICES = [
        (1, "First Year"),
        (2, "Second Year"),
        (3, "Third Year"),
        (4, "Fourth Year"),
    ]

    EXAM_TYPE_CHOICES = [
        ("CAT1", "CAT 1"),
        ("CAT2", "CAT 2"),
    ]

    subject = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=4, choices=EXAM_TYPE_CHOICES, default="CAT1")
    year = models.IntegerField(choices=YEAR_CHOICES)
    staff_name = models.CharField(max_length=255)
    question_paper = models.FileField(upload_to='question_papers/')
    answer_key = models.FileField(upload_to='answer_keys/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {dict(self.YEAR_CHOICES).get(self.year, 'Unknown')} - {self.get_exam_type_display()}"


class ExamSubmission(models.Model):
    EXAM_TYPES = [
        ('CAT1', 'CAT 1'),
        ('CAT2', 'CAT 2'),
    ]

    YEARS = [
        (1, "First Year"),
        (2, "Second Year"),
        (3, "Third Year"),
        (4, "Fourth Year"),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)  # Remove null=True, blank=True
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    year = models.CharField(max_length=1, choices=YEARS)
    staff_name = models.CharField(max_length=100)
    answer_sheet = models.FileField(upload_to='answer_sheets/', null=True, blank=True)
    is_graded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - {self.exam_type} ({self.get_year_display()})"


class EvaluationResult(models.Model):
    submission = models.OneToOneField(
        ExamSubmission, 
        on_delete=models.CASCADE, 
        related_name="evaluation"
    )
    evaluated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="evaluations"
    )
    formatted_report = models.TextField()  # Stores only the human-readable report
    total_score = models.FloatField(default=0.0)
    max_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        exam_subject = self.submission.exam.subject if self.submission.exam else "Unknown Exam"
        return f"Evaluation for {self.submission.student.username} - {exam_subject}"

class APIKey(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="A name to identify the API key (e.g., Google, OpenAI).")
    key = models.TextField(help_text="The actual API key string.")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, help_text="Indicates if the key is currently in use.")

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"