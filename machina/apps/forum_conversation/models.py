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


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_content = models.CharField(max_length=100)
    notification_link = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class Post(AbstractPost):
    __original_flags = None
    __original_votes = None

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.__original_flags = self.flag_count
        self.__original_votes = self.vote_count

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        super(Post, self).save(force_insert, force_update, *args, **kwargs)

        notification_link = "/forum/{}-{}/topic/{}-{}/?post={}#{}".format(self.topic.forum.slug, self.topic.forum.id, self.topic.slug, self.topic.id, self.id, self.id)
        if self.__original_flags != self.flag_count:
            n = UserNotification(user=self.poster, notification_content="Flag updates on post {}".format(self.subject), notification_link=notification_link)
            n.save()

        if self.__original_votes != self.vote_count:
            n = UserNotification(user=self.poster, notification_content="Vote update on post {}".format(self.subject), notification_link=notification_link)
            n.save()

        self.__original_flags = self.flag_count
        self.__original_votes = self.vote_count

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

@receiver(post_save, sender=Post)
def make_notifications(sender, instance, created, **kwargs):
    user = instance.topic.poster
    notification_content = "You have a new notification"
    notification_link = "/forum/{}-{}/topic/{}-{}/?post={}#{}".format(instance.topic.forum.slug, instance.topic.forum.id, instance.topic.slug, instance.topic.id, instance.id, instance.id)

    if created:
        notification_content = "A new post was created on your topic {}".format(instance.topic.slug)
    else:
        notification_content = "A post's contetn was edited on your topic {}".format(instance.topic.slug)

    n = UserNotification(user=user, notification_link=notification_link, notification_content=notification_content)
    n.save()
