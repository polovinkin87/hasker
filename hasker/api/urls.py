from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import views


app_name = "api"

questions_patterns = ([
    path("", views.IndexQuestionListView.as_view(), name="index"),
    path("top/", views.TopQuestionListView.as_view(), name="top"),
    path("search/", views.SearchQuestionListView.as_view(), name="search"),
    path("<int:q_id>/", views.QuestionDetailView.as_view(), name="detail"),
    path("<int:q_id>/answers/", views.AnswerListView.as_view(), name="answers"),
], "question")

token_patterns = ([
    path("", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("verify/", TokenVerifyView.as_view(), name='token_verify'),
], "token")

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("token/", include(token_patterns)),
    path("questions/", include(questions_patterns)),
    path("swagger/", schema_view.with_ui('swagger', cache_timeout=0))
]