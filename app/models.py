import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils import timezone


class User(AbstractUser):
    # avatar = models.FileField(upload_to='64x64.png')
    avatar = models.ImageField(default="default/64x64.png", verbose_name="User's Avatar")


def validate_rate(value):
    if value > 1 or value < -1:
        raise ValidationError('Rate value error', params={'value': value})


class Rate(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    is_like = models.SmallIntegerField(default=0, validators=[validate_rate])

    class Meta:
        abstract = True


class QuestionManager(models.Manager):
    def fresh(self):
        return self.order_by('-pub_date')

    def hot(self):
        return self.order_by('-rating')

    def tag_question(self, tname):
        return self.filter(tags__tag_name__in=[tname]).distinct()


class Question(models.Model):
    title = models.CharField(max_length=200)
    definition = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')
    rating = models.IntegerField(default=0, null=False, verbose_name="Question's Rating")

    objects = QuestionManager()

    def __str__(self):
        return self.title


class QuestionRate(Rate):
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'user')


class AnswerManager(models.Manager):
    def best(self):
        return self.order_by('-likes')


class Answer(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    status_correct = models.BooleanField(default=False)
    rating = models.IntegerField(default=0, null=False, verbose_name="Answer's Rating")

    objects = AnswerManager()

    def __str__(self):
        return self.id, self.author, self.question


class QuestionRateManager(models.Manager):
    def islike(self, uid, qid):
        return self.get(user_id=uid, question_id=qid)


class AnswerRate(Rate):
    answer = models.ForeignKey('Answer', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('answer', 'user')


class TagManager(models.Manager):
    def best(self):
        return self.order_by('id')


class Tag(models.Model):
    tag_name = models.CharField(max_length=20)
    objects = TagManager()

    def __str__(self):
        return self.tag_name






