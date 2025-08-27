from django.db import models
from django.contrib.auth.models import User

# Job model posted by recruiters
class Job(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posted_jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title

# Job application model (Candidate applies to a Job)
class Application(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} applied to {self.job.title}"
