from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token as AuthToken


class Token(AuthToken):
    """ Custom token model - extension for drf.authtoken Token """
    key = models.CharField("Key", max_length=40, db_index=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name="User",
    )
    is_active = models.BooleanField(default=True)


class TokenProxy(Token):
    """
    Extension - proxy mapping pk to user pk for use in admin.
    """
    @property
    def pk(self):
        return self.user_id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
