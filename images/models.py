from django.contrib.auth.models import User
from django.db import models

# Model for Features
class Feature(models.Model):
    name = models.CharField(max_length=50)
    pixels = models.IntegerField(null=True)

    def __str__(self) -> str:
        return self.name

# Model for Plans
class Plan(models.Model):
    name = models.CharField(max_length=20)
    features = models.ManyToManyField(Feature)

    def __str__(self) -> str:
        return self.name

# Model for combining Users with Plans
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name="users")

    def __str__(self) -> str:
        return self.user.get_username()

# Model for Images
class Image(models.Model):
    user = models.ForeignKey("UserProfile", on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="images/")
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True)
