from django.db import models


class Device(models.Model):
    generated_id = models.CharField(max_length=200, unique=True, default="")
    name = models.CharField(max_length=200, default="")
    parent_name = models.CharField(max_length=200, default="")
    latitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.0)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, default=0.0)

    def __str__(self):
        return f"{self.generated_id}"


class TeamMember(models.Model):
    generated_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    github_link = models.CharField(max_length=200, null=True, blank=True)
    linkedin_link = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to="team", null=True, blank=True)

    def __str__(self):
        return f"{self.generated_id}"
