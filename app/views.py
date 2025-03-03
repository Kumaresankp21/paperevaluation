from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EvaluationResult, ExamSubmission,Exam
from .evaluation.ocr import generate_ocr
from .evaluation.extract_question_answerkey import question_answer_content
from .evaluation.preprocess_ocr import preprocess_ocr_question_wise
from .evaluation.evalution import evaluate_exam_with_ocr_to_json
from .evaluation.report import generate_report

def home(request):
    return render(request, 'home.html')


def signup_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use!")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'authentication/signup.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'authentication/login.html')


def student_dashboard(request):
    exams = ExamSubmission.objects.filter(student=request.user)  # Fetch exams created by logged-in student
    return render(request, 'dashboard/student/student_dashboard.html', {'exams': exams})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')


def student_exam_fill(request):
    if request.method == "POST":
        subject = request.POST['subject']
        exam_type = request.POST['exam_type']
        year = request.POST['year']
        staff_name = request.POST['staff_name']

        ExamSubmission.objects.create(
            student=request.user,
            subject=subject,
            exam_type=exam_type,
            year=year,
            staff_name=staff_name
        )

        messages.success(request, "Exam details submitted successfully!")
        return redirect('student_dashboard')

    return render(request, 'dashboard/student/exam_fill.html')


def teacher_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:  # Allow only superusers
                login(request, user)
                messages.success(request, "Welcome, Teacher!")
                return redirect("teacher_dashboard")  # Redirect to teacher dashboard
            else:
                messages.error(request, "Access Denied! Only teachers (superusers) can log in.")
        else:
            messages.error(request, "Invalid Username or Password!")

    return render(request, "dashboard/teacher/teacher_login.html")

@login_required
def teacher_dashboard(request):
    if not request.user.is_superuser:
        return redirect("home")  # Redirect unauthorized users

    exams = Exam.objects.all().order_by("-id")  # Fetch all exams
    return render(request, "dashboard/teacher/teacher_dashboard.html", {"exams": exams})

@login_required
def create_exam(request):
    if not request.user.is_superuser:
        messages.error(request, "❌ Unauthorized access!")
        return redirect("home")

    if request.method == "POST":
        subject = request.POST.get("subject")
        exam_type = request.POST.get("exam_type")
        year = request.POST.get("year")
        staff_name = request.POST.get("staff_name")
        question_paper = request.FILES.get("question_paper")
        answer_key = request.FILES.get("answer_key")

        if not all([subject, exam_type, year, staff_name, question_paper, answer_key]):
            messages.error(request, "⚠️ All fields are required!")
            return redirect("create_exam")

        Exam.objects.create(
            subject=subject,
            exam_type=exam_type,
            year=year,
            staff_name=staff_name,
            question_paper=question_paper,
            answer_key=answer_key
        )

        messages.success(request, "✅ Exam successfully created!")
        return redirect("teacher_dashboard")

    return render(request, "dashboard/teacher/create_exam.html")

@login_required
def view_submissions(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    submissions = ExamSubmission.objects.filter(year=exam.year)

    if request.method == "POST":
        for submission in submissions:
            file_field_name = f"answer_sheet_{submission.id}"
            if file_field_name in request.FILES:
                if submission.answer_sheet:
                    messages.warning(request, f"⚠️ Answer sheet for {submission.student.username} already uploaded.")
                else:
                    submission.answer_sheet = request.FILES[file_field_name]
                    submission.save()
                    messages.success(request, f"✅ Answer sheet uploaded for {submission.student.username}.")

        return redirect('view_submissions', exam_id=exam.id)

    return render(request, "dashboard/teacher/view_submissions.html", {"exam": exam, "submissions": submissions})

def evaluate_submission_view(request, submission_id):
    submission = get_object_or_404(ExamSubmission, id=submission_id)

    # 1️⃣ Extract OCR text from uploaded answer sheet
    ocr_text = generate_ocr(submission.answer_sheet.path)

    # 2️⃣ Extract question paper and answer key
    question_paper_text = question_answer_content(submission.exam.question_paper.path)
    answer_key_text = question_answer_content(submission.exam.answer_key.path)

    # 3️⃣ Preprocess OCR text to align with question numbers
    structured_ocr_text = preprocess_ocr_question_wise(ocr_text, question_paper_text)

    # 4️⃣ Evaluate answers using Gemini API
    evaluation_result_json = evaluate_exam_with_ocr_to_json(structured_ocr_text, answer_key_text)

    # 5️⃣ Generate a detailed report
    formatted_report = generate_report(evaluation_result_json)

    # 6️⃣ Extract total score and max score from JSON
    import json
    evaluation_result_json = evaluation_result_json.strip("`")
    print(evaluation_result_json)
    evaluation_data = json.loads(evaluation_result_json)
    total_score = sum(q["marks_awarded"] for q in evaluation_data["questions"])
    max_score = sum(q["max_marks"] for q in evaluation_data["questions"])

    # 7️⃣ Save the evaluation result in a separate model
    evaluation, created = EvaluationResult.objects.update_or_create(
        submission=submission,
        defaults={
            "evaluated_by": request.user,
            "json_result": evaluation_data,
            "formatted_report": formatted_report,
            "total_score": total_score,
            "max_score": max_score,
        },
    )

    messages.success(request, "Evaluation completed successfully!")
    return redirect('view_submissions', exam_id=submission.exam.id)