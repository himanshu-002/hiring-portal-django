from django.urls import path, include
from rest_framework import routers
from apis import views

router = routers.SimpleRouter()
router.register(
    r'candidates',
    views.CandidateViewSet,
    basename="candidates"
)
router.register(
    r'interview',
    views.InterviewListRetrieveViewSet,
    basename="interview-list-retrieve"
)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path(
        'api/v1/skill/add/',
        views.SkillAPIView.as_view(),
        name="skill-create"
    ),
    path(
        'api/v1/interview/assign/',
        views.HRAssignInterviewApiView.as_view(),
        name="interview-create"
    ),
    path(
        'api/v1/employee/add/',
        views.EmployeeViewSet.as_view({'post': 'create'}),
        name="employee-create"
    ),
    path(
        'api/v1/employee/edit/<int:pk>/',
        views.EmployeeViewSet.as_view({'put': 'update'}),
        name="employee-edit"
    ),
    path(
        'api/v1/interview/action/<str:job_id>/',
        views.InterviewActionAPIView.as_view(),
        name="interview-action"
    ),
    path(
        'api/v1/interview/<str:job_id>/round/<int:round_no>/',
        views.InterviewRoundDetailAPIView.as_view(),
        name="round-detail-and-edit"
    ),
]
