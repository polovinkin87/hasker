from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    registered = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(verbose_name='Avatar', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'username': self.username})
