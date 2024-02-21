from django import template
from django.conf import settings
from django.db.models import Count

from ..models import Question

register = template.Library()


@register.simple_tag
def top_questions():
    questions = Question.objects.all().annotate(
        likes=Count("user_q_like"),
    ).order_by("-likes", "-created")[:settings.PAGINATE_QUESTIONS]
    return questions
