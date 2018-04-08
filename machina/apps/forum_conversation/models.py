# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from machina.apps.forum_conversation.abstract_models import AbstractPost
from machina.apps.forum_conversation.abstract_models import AbstractTopic
from machina.core.db.models import model_factory
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


Topic = model_factory(AbstractTopic)
Post = model_factory(AbstractPost)

class Userflags(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    flag_count = models.PositiveIntegerField(
        verbose_name=_('Flag count'), editable=False, blank=True, default=0)

@receiver(post_save, sender=User)
def create_userflags(sender, instance, created, **kwargs):
    if created:
        Userflags.objects.create(user=instance)  

@receiver(post_save, sender=User)
def save_userflags(sender, instance, **kwargs):
    instance.userflags.save()        
