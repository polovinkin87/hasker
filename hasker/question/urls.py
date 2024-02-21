from django.urls import path
from . import views

app_name = 'question'

urlpatterns = [
    path('', views.redirect_question, name='home'),
    path('question/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('question/<str:slug>/', views.QuestionDetailView.as_view(), name='question_detail'),
    path('questions/', views.QuestionListView.as_view(title='Top questions:'), name='question_list'),
    path('tag_autocomplete/', views.tag_autocomplete, name='tag_add'),
    path('tag/<str:slug>/', views.QuestionListView.as_view(), name='tag_detail'),
    path('search/', views.QuestionListView.as_view(), name='search'),
    path('question/<str:slug>/q_add_likes/', views.QuestionAddLikes.as_view(), name='question_add_likes'),
    path('question/<str:slug>/q_del_likes/', views.QuestionDelLikes.as_view(), name='question_del_likes'),
    path('question/<str:slug>/a_add_likes/<int:pk>/', views.AnswerAddLikes.as_view(), name='answer_add_likes'),
    path('question/<str:slug>/a_del_likes/<int:pk>/', views.AnswerDelLikes.as_view(), name='answer_del_likes'),
    path('question/correct_answer/<int:pk>/', views.correct_answer, name='correct_answer'),
]
