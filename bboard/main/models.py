from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True,
                                        verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Оповещать при новых комментариях?')
    class Meta(AbstractUser.Meta):
        pass

user_registreted = Signal("instance")

def user_registreted_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])

user_registreted.connect(user_registreted_dispatcher)

class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, unique=True,
                            verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True,
                                        verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric',
                                        on_delete=models.PROTECT, null=True, blank=True,
                                        verbose_name='Надрубрика')

class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)

class SuperRubric(Rubric):
    object = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name')
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'

class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)

class SubRubric(Rubric):
    object = SubRubricManager()

    def __str__(self):
        return '%s - %s' % (self.super_rubric, self.name)

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'