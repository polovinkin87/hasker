from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.http import (
    HttpResponseNotFound, HttpResponseBadRequest,
    HttpResponseForbidden, HttpResponseRedirect
)

from users.models import User
from question.models import Question, Tag, UserQuestionRelation


class IndexViewTests(TestCase):
    questions = {}

    def setUp(self):
        test_user = User.objects.create_user(
            username="test1",
            email="test1@mail.com",
            password="password"
        )

        self.questions["question_1"] = Question.objects.create(
            title="question_1",
            text="question_1",
            author=test_user,
            created=datetime.today() - timedelta(days=2)
        )
        self.questions["question_1"].save()

        self.questions["question_2"] = Question.objects.create(
            title="question_2",
            text="question_2",
            author=test_user,
            created=datetime.today() - timedelta(days=1)
        )
        self.questions["question_2"].save()

        self.questions["question_3"] = Question.objects.create(
            title="question_3",
            text="question_3",
            author=test_user,
            created=datetime.today()
        )
        self.questions["question_3"].save()

    def test_questions_sorted_by_pub_date(self):
        response = self.client.get(reverse("question:question_list"))

        self.assertListEqual(
            list(response.context["questions"]),
            [
                self.questions["question_3"],
                self.questions["question_2"],
                self.questions["question_1"]
            ]
        )


class SearchViewTests(TestCase):
    questions = {}

    def setUp(self):
        test_user = User.objects.create_user(
            username="test1",
            email="test1@mail.com",
            password="password"
        )

        test_tag = Tag.objects.create(title="foo")

        self.questions["question_1"] = Question.objects.create(
            title="footitle",
            text="footext",
            author=test_user,
        )
        self.questions["question_1"].tags.add(test_tag)
        self.questions["question_1"].save()

        self.questions["question_2"] = Question.objects.create(
            title="bartitle",
            text="bartext",
            author=test_user,
        )
        self.questions["question_2"].save()

    def test_search_by_empty_query(self):
        response = self.client.get(
            reverse("question:search"), follow=True
        )

        self.assertEqual(
            response.status_code, HttpResponseBadRequest.status_code
        )

    def test_search_by_empty_tag(self):
        response = self.client.get(
            reverse("question:search") + "?search=tag:", follow=True
        )
        self.assertEqual(
            response.status_code, HttpResponseBadRequest.status_code
        )

    def test_search_by_not_exist_tag(self):
        response = self.client.get(
            reverse("question:search") + "?search=tag:badtag", follow=True
        )
        self.assertEqual(
            response.status_code, HttpResponseNotFound.status_code
        )

    def test_search_by_phrase_empty_results(self):
        response = self.client.get(
            reverse("question:search") + "?search=badphrase", follow=True
        )
        self.assertEqual(
            response.status_code, 200
        )
        self.assertListEqual(
            list(response.context["questions"]),
            []
        )

    def test_search_by_title(self):
        response = self.client.get(
            reverse("question:search") + "?search=footitle", follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["questions"]),
            [self.questions["question_1"]]
        )

    def test_search_by_text(self):
        response = self.client.get(
            reverse("question:search") + "?search=bartext", follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["questions"]),
            [self.questions["question_2"]]
        )

    def test_search_by_tag(self):
        response = self.client.get(
            reverse("question:search") + "?search=tag:foo", follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            list(response.context["questions"]),
            [self.questions["question_1"]]
        )


class LikeViewTests(TestCase):

    def setUp(self):
        self.credentials = {
            "username": "test", "password": "password"
        }
        self.credentials_2 = {
            "username": "test2", "password": "password"
        }
        self.user = User.objects.create_user(**self.credentials)
        self.user_2 = User.objects.create_user(**self.credentials_2)

        self.question = Question.objects.create(
            title="question_1",
            text="question_1",
            author=self.user_2,
            created=datetime.today() - timedelta(days=2)
        )
        self.question.save()

    def test_unauthorized_user_cant_vote_for_question_code(self):
        response = self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.assertEqual(
            response.status_code, HttpResponseRedirect.status_code
        )

    def test_unauthorized_user_cant_vote_for_question_url(self):
        response = self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.assertEqual(
            response.url[:39], '/users/login/?next=/question/question_1'
        )

    def test_authorized_user_cant_vote_for_question_code(self):
        self.client.login(**self.credentials)
        response = self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.assertEqual(
            response.status_code, HttpResponseRedirect.status_code
        )

    def test_authorized_user_cant_vote_for_question_url(self):
        self.client.login(**self.credentials)
        response = self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.assertEqual(
            response.url[:20], '/question/question_1'
        )

    def test_vote_can_not_vote_own_object(self):
        self.client.login(**self.credentials_2)
        response = self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.assertEqual(
            response.status_code, HttpResponseForbidden.status_code
        )

    def test_vote_user_can_toggle(self):
        self.client.login(**self.credentials)

        self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )
        self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )

        q_votes = UserQuestionRelation.objects.all().count()

        self.assertEqual(q_votes, 1)

    def test_vote_user_can_like_than_dislike(self):
        self.client.login(**self.credentials)

        q_votes_start = UserQuestionRelation.objects.all().count()

        self.client.get(
            reverse("question:question_add_likes", kwargs={"slug": self.question.slug}),
        )

        self.client.get(
            reverse("question:question_del_likes", kwargs={"slug": self.question.slug}),
        )

        q_votes_end = UserQuestionRelation.objects.all().count()

        self.assertEqual(q_votes_start, q_votes_end)
