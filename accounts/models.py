from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class CustomUser(AbstractUser):
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
