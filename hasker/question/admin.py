from django.contrib import admin
from django.contrib.admin import ModelAdmin

from . import models


@admin.register(models.Question)
class QuestionAdmin(ModelAdmin):
    pass


@admin.register(models.Answer)
class AnswerAdmin(ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(ModelAdmin):
    pass


@admin.register(models.UserQuestionRelation)
class UserQuestionRelationAdmin(ModelAdmin):
    pass


@admin.register(models.UserAnswerRelation)
class UserAnswerRelationAdmin(ModelAdmin):
    pass
