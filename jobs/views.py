from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .models import Job, Application


@csrf_exempt
def signup(request):
    if request.method == "POST":

        data = json.loads(request.body.decode())

        email = data.get("email")
        password = data.get("password")
        username = email
        role = data.get("role", "candidate")       

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "User already exists"}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = role
        user.save()

        return JsonResponse({"message": f"{role} registered successfully!"})


@csrf_exempt
def user_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            email = data.get("email")
            password = data.get("password")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        if not email or not password:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        user = authenticate(username=email, password=password)

        if user:
            login(request, user)
            return JsonResponse({"message": "Login successful", "role": user.first_name})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({"error": "POST request required"}, status=405)


@login_required
def user_logout(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"})



def job_list(request):
    jobs = Job.objects.all().values("id", "title", "description", "recruiter__username")
    return JsonResponse(list(jobs), safe=False)


@csrf_exempt
def apply_job(request):
    if request.method == "POST":
            data = json.loads(request.body.decode("utf-8"))
            job_id = data.get("job_id")
            candidate_email = data.get("email")
            candidate_username = data.get("username")

    if not job_id or not candidate_email:
        return JsonResponse({"error": "job_id and email are required"}, status=400)

    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return JsonResponse({"error": "Job not found"}, status=404)

    candidate, _ = User.objects.get_or_create(username=candidate_username or candidate_email,defaults={"email": candidate_email, "first_name": "Candidate"})

    Application.objects.create(candidate=candidate, job=job)

    # send_mail(
    #     subject="Job Application Submitted",
    #     message=f"You applied to {job.title}",
    #     from_email="noreply@jobportal.com",
    #     recipient_list=[candidate_email],
    # )

    # send_mail(
    #     subject="New Applicant",
    #     message=f"{candidate.username} applied to your job {job.title}",
    #     from_email="noreply@jobportal.com",
    #     recipient_list=[job.recruiter.email],
    # )

    return JsonResponse({"message": "Application submitted successfully!"}, status=201)



def applied_jobs(request):
    apps = Application.objects.filter(candidate=request.user).select_related("job")
    data = [{"job_id": a.job.id, "title": a.job.title, "description": a.job.description} for a in apps]
    return JsonResponse(data, safe=False)



@csrf_exempt
def post_job(request):
    if request.method == "POST":
        data = json.loads(request.body.decode())

        if data.get("first_name") != "recruiter":
            return JsonResponse({"error": "Only recruiters can post jobs"}, status=403)

        title = data.get("title")
        description = data.get("description")
        #temp
        recruiter = User.objects.filter(first_name="recruiter").first()
        if not recruiter:
            return JsonResponse({"error": "No recruiter found"}, status=404)

        job = Job.objects.create(recruiter=recruiter, title=title, description=description)
        return JsonResponse({"message": "Job posted successfully", "job_id": job.id})

    return JsonResponse({"error": "POST request required"}, status=405)


def view_applicants(request):
    data = json.loads(request.body.decode())
    if data.get("first_name") != "recruiter":
        return JsonResponse({"error": "Only recruiters can view applicants"})
    
    jobs = Job.objects.filter(recruiter=request.user).prefetch_related("applications__candidate")
    data = []
    for job in jobs:
        applicants = [app.candidate.username for app in job.applications.all()]
        data.append({"job_title": job.title, "applicants": applicants})
    return JsonResponse(data, safe=False)
