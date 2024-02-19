from time import time
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def gen_slug(title):
    new_slug = slugify(title, allow_unicode=True)
    return new_slug + '-' + str(int(time()))


class AbstractQA(models.Model):
    text = models.TextField(max_length=5000, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True
        ordering = ['-created']


class Tag(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def get_absolute_url(self):
        return reverse('tag_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.title}'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    @classmethod
    def get_or_create(cls, value):
        slug = gen_slug(value.lower().strip())
        if cls.objects.filter(title=value).exists():
            return cls.objects.get(title=value)
        else:
            return cls.objects.create(title=value.lower().strip())


class Question(AbstractQA):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='questions')
    correct_answer = models.OneToOneField('Answer', blank=True, null=True, on_delete=models.CASCADE,
                                          related_name='answer_1')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserQuestionRelation',
                                   related_name='user_questions')

    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)


class Answer(AbstractQA):
    question = models.ForeignKey('Question', related_name='answers', on_delete=models.CASCADE)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserAnswerRelation', related_name='user_answers')

    def __str__(self):
        return f'{self.text[:50]}'


class UserQuestionRelation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('Question', related_name='user_q_like', on_delete=models.CASCADE)
    like = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author}: {self.question}, {self.like}'

    class Meta:
        unique_together = ['author', 'question']


class UserAnswerRelation(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    answer = models.ForeignKey('Answer', related_name='user_a_like', on_delete=models.CASCADE)
    like = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author}: {self.answer}, {self.like}'

    class Meta:
        unique_together = ['author', 'answer']
