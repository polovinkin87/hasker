from rest_framework import serializers

from question.models import Question, Answer


class QuestionListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:question:detail", lookup_url_kwarg="q_id"
    )

    class Meta:
        model = Question
        fields = ("id", "url",)


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="username"
    )
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title"
    )
    answers = serializers.HyperlinkedIdentityField(
        many=False, read_only=True,
        view_name="api:question:answers", lookup_url_kwarg="q_id"
    )
    answers_count = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id", "title", "text", "author", "created",
            "tags", "answers", "answers_count"
        )

    def get_answers_count(self, question):
        return question.answers.count()


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="username"
    )

    class Meta:
        model = Answer
        fields = (
            "id", "text", "author", "created"
        )
