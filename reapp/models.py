from django.conf import settings
from django.db import models


class UserProfile(models.Model):
	"""Extended information captured during Technoheaven onboarding."""

	GENDER_CHOICES = (
		("Female", "Female"),
		("Male", "Male"),
		("Other", "Other"),
	)

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	full_name = models.CharField(max_length=150)
	country = models.CharField(max_length=100)
	age = models.PositiveSmallIntegerField(blank=True, null=True)
	gender = models.CharField(max_length=32, choices=GENDER_CHOICES, blank=True)
	contact_number = models.CharField(max_length=50, blank=True)
	terms_accepted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:  # pragma: no cover - trivial representation
		return f"Profile of {self.user.username}"
