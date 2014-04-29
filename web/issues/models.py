from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Issue(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.title
