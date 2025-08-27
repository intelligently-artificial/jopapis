# from django.urls import path
# from . import views

# urlpatterns = [
#     path("signup/", views.signup),
#     path("login/", views.user_login),
#     path("logout/", views.user_logout),
#     path("jobs/", views.job_list),
#     path("apply/", views.apply_job),
#     path("applied/", views.applied_jobs),
# ]


from django.urls import path
from . import views

urlpatterns = [
    # Common
    path("signup/", views.signup, name="signup"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Candidate
    path("jobs/", views.job_list, name="job_list"),
    path("apply/", views.apply_job, name="apply_job"),
    path("applied/", views.applied_jobs, name="applied_jobs"),

    # Recruiter
    path("post-job/", views.post_job, name="post_job"),
    path("applicants/", views.view_applicants, name="view_applicants"),
]





