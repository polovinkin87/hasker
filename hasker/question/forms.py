from functools import partial

from django.db import transaction
from django.forms import ModelForm, ValidationError, TextInput, HiddenInput, Field
from django.conf import settings
from django.core.mail import send_mail
from django.utils.text import Truncator

from .models import Question, Tag, Answer


class TagitWidget(HiddenInput):
    """ Widget on the basis of Tag-It! http://aehlke.github.com/tag-it/"""

    class Media:
        js = (settings.STATIC_URL + 'js/tagit_widget.js', settings.STATIC_URL + 'js/tag-it.js',)
        css = {"all": (settings.STATIC_URL + 'css/jquery.tagit.css',)}


class TagitField(Field):
    """ Tag field """

    widget = TagitWidget

    def __init__(self, tag_model, *args, **kwargs):
        self.tag_model = tag_model
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        tag_strings = value.split(',')
        return [self.tag_model.get_or_create(tag_string) for tag_string in tag_strings if len(tag_string) > 0]

    def validate(self, value):
        if len(value) == 0 and self.required:
            raise ValidationError(self.error_messages['required'])

    def prepare_value(self, value):
        if value is not None and hasattr(value, '__iter__'):
            return ','.join((tag for tag in value))
        return value

    def widget_attrs(self, widget):
        res = super(TagitField, self).widget_attrs(widget) or {}
        res["class"] = "tagit"
        return res


class AnswerForm(ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)

    widgets = {
        'text': TextInput(attrs={'class': 'form-control'}),
    }

    @transaction.atomic
    def save(self, commit=True):
        answer = super().save(commit)
        transaction.on_commit(partial(self.notify_question_author, answer))
        return answer

    @staticmethod
    def notify_question_author(answer):
        title_truncated = Truncator(answer.question.title)

        subject = "A new answer to the question {} - Hasker".format(
            title_truncated.words(5)
        )
        message = """
            <p>Received a new response from the user {answer_author}
            to your question <a href="{q_url}">{q_title}</a>:</p>
            <p>{a_text}</p>
        """.format(
            answer_author=answer.author.username,
            q_url=answer.question.url,
            q_title=title_truncated.words(10),
            a_text=Truncator(answer.text).words(25)
        )
        from_email = settings.TECH_EMAIL
        recipient_list = [answer.author.email]

        send_mail(
            subject, message, from_email, recipient_list, fail_silently=True
        )


class QuestionForm(ModelForm):
    tags = TagitField(Tag, label='Tags', required=True)

    class Meta:
        model = Question
        fields = ("title", "text", "tags")

    widgets = {
        'title': TextInput(attrs={'class': 'form-control'}),
        'text': TextInput(attrs={'class': 'form-control'}),
        'tags': tags,
    }

    @transaction.atomic
    def save(self, commit=True):
        return super().save(commit)

    # def clean_tags(self):
    #     tags = self.cleaned_data["tags"]
    #     if len(tags) > 3:
    #         raise ValidationError(
    #             "Maximum number of tags - 3",
    #             code="exceeding_tags_limit"
    #         )
    #     return tags
