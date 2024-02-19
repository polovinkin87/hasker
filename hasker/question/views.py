import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import resolve
from django.views import View
from django.views.generic import CreateView, DetailView, ListView
from django.db.models import Q

from users.models import User
from .models import Question, Tag, UserQuestionRelation, UserAnswerRelation, Answer
from .forms import QuestionForm, AnswerForm


class QuestionCreateView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'question/create.html'
    login_url = 'users:login'

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New question"
        return context


class QuestionDetailView(DetailView):
    model = Question
    object = None
    template_name = 'question/detail.html'
    context_object_name = 'question'
    slug_url_kwarg = 'slug'

    answers_paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        answers_page = self.request.GET.get("page", 1)
        answers = self.object.answers.all().order_by('-update')
        answers_paginator = paginator.Paginator(
            answers, self.answers_paginate_by
        )

        try:
            answers_page_obj = answers_paginator.page(answers_page)
        except (paginator.PageNotAnInteger, paginator.EmptyPage):
            answers_page_obj = answers_paginator.page(1)

        context["answers_page_obj"] = answers_page_obj
        context["answers"] = answers_page_obj.object_list
        context["form"] = AnswerForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        user_is_auth = request.user.is_authenticated
        user_not_author = request.user != self.object.author
        user_can_add_answer = user_is_auth and user_not_author
        if not user_can_add_answer:
            return super().get(request, *args, **kwargs)

        form = AnswerForm(request.POST)
        if form.is_valid():
            self.object.answers.create(
                text=form.cleaned_data['text'],
                author=request.user,
                question=self.object
            )
            redirect(request.path)

        context = self.get_context_data(object=self.object)
        context["form"] = form
        return self.render_to_response(context)


class QuestionListView(ListView):
    context_object_name = 'questions'
    template_name = 'question/list.html'
    paginate_by = 3
    search_query = ''
    title = ''
    sort_by_time = False
    tag_slug = ''

    def dispatch(self, request, *args, **kwargs):
        url_name = resolve(self.request.path).url_name

        if url_name == 'tag_detail':
            self.tag_slug = self.kwargs.get('slug', "")
            self.title = f'Tag: {self.tag_slug}'
        elif url_name == 'search':
            self.search_query = self.request.GET.get('search')
            if not self.search_query:
                return HttpResponseBadRequest('Empty search query')
            self.title = f'Search results: {self.search_query}'
            if self.search_query.startswith('tag:'):
                tag_title = self.search_query[4:]
                if not tag_title:
                    return HttpResponseBadRequest('Empty tag')
                slug = Tag.objects.get(title__icontains=tag_title)
                return redirect('tag_detail', slug=slug)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.search_query:
            questions = Question.objects.filter(
                Q(title__icontains=self.search_query) | Q(text__icontains=self.search_query))
        elif self.tag_slug:
            tag = get_object_or_404(Tag, slug=self.tag_slug)
            questions = tag.questions.all()
        else:
            questions = Question.objects.all()

        return questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['tag'] = self.tag_slug
        return context


def redirect_question(request):
    return redirect('question_list', permanent=True)


# def add_tag(request):
#     tag_val = request.GET.get('tag', None)
#     tag_val = tag_val.lower()
#     new_tag = Tag.objects.get_or_create(title=tag_val)
#     return HttpResponse(new_tag[0].title)


def tag_autocomplete(request):
    value = request.GET['term']
    available_tags = Tag.objects.filter(title__startswith=value.lower())
    response = HttpResponse(json.dumps([tag.title for tag in available_tags]), content_type="application/json")
    return response


class QuestionAddLikes(LoginRequiredMixin, View):
    login_url = 'users:login'

    def get(self, request, slug):
        try:
            UserQuestionRelation.objects.get(author=request.user,
                                             question=Question.objects.get(slug=slug).pk)
            return redirect('question_detail', slug=slug)
        except:
            if Question.objects.get(slug=slug).author == request.user:
                return HttpResponseForbidden("Can't vote own question/answer")
            new_like = UserQuestionRelation()
            new_like.author = request.user
            new_like.question = Question.objects.get(slug=slug)
            new_like.save()
            return redirect('question_detail', slug=slug)


class QuestionDelLikes(LoginRequiredMixin, View):
    login_url = 'users:login'

    def get(self, request, slug):
        try:
            like = UserQuestionRelation.objects.get(author=request.user,
                                                    question=Question.objects.get(slug=slug).pk)
            like.delete()
            return redirect('question_detail', slug=slug)
        except:
            return redirect('question_detail', slug=slug)


class AnswerAddLikes(LoginRequiredMixin, View):
    login_url = 'users:login'

    def get(self, request, slug, pk):
        try:
            UserAnswerRelation.objects.get(author=request.user,
                                             answer=Answer.objects.get(pk=pk).pk)
            return redirect('question_detail', slug=slug)
        except:
            if Answer.objects.get(pk=pk).author == request.user:
                return HttpResponseForbidden("Can't vote own question/answer")
            new_like = UserAnswerRelation()
            new_like.author = request.user
            new_like.answer = Answer.objects.get(pk=pk)
            new_like.save()
            return redirect('question_detail', slug=slug)


class AnswerDelLikes(LoginRequiredMixin, View):
    login_url = 'users:login'

    def get(self, request, slug, pk):
        try:
            like = UserAnswerRelation.objects.get(author=request.user,
                                                    answer=Answer.objects.get(pk=pk).pk)
            like.delete()
            return redirect('question_detail', slug=slug)
        except:
            return redirect('question_detail', slug=slug)


def correct_answer(request, pk):
    try:
        answer = Answer.objects.get(pk=pk)
    except (ObjectDoesNotExist,):
        return HttpResponseBadRequest()

    answer.question.correct_answer = answer
    answer.question.save()

    return redirect(answer.question.get_absolute_url())

