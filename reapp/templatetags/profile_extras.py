from __future__ import annotations

from django import template
from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.simple_tag
def get_user_profile(user):
    """Safely return the related profile for an authenticated user."""
    if not getattr(user, "is_authenticated", False):
        return None
    try:
        return user.profile
    except ObjectDoesNotExist:  # UserProfile.DoesNotExist without circular import
        return None


@register.filter(name="startswith")
def startswith(text, prefix):
    """Return True if 'text' starts with the given 'prefix'.

    Useful in templates: {% if request.path|startswith:some_url %}
    """
    try:
        return str(text).startswith(str(prefix))
    except Exception:
        return False
