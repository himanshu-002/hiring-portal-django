import json
from json import JSONDecodeError
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.generics import (
    CreateAPIView,
    get_object_or_404,
    RetrieveUpdateAPIView
)
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apis.models import (
    Employee,
    CandidateInfo,
    Interview,
    InterviewRound
)
from apis.permissions import IsAdminOrHrEmployee, IsAdmin, IsHrEmployee
from apis.serializers import (
    SkillSerializer,
    EmployeeSerializer,
    CandidateInfoSerializer,
    HRAssignInterviewSerializer,
    ActionSerializer,
    InterviewRoundSerializer,
    InterviewSerializer
)
from apis.utils import is_valid_action


class SkillAPIView(CreateAPIView):
    permission_classes = [IsAdminOrHrEmployee]
    serializer_class = SkillSerializer
    http_method_names = ['post']


class EmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrHrEmployee]
    model = Employee
    serializer_class = EmployeeSerializer
    http_method_names = ["post", "put"]
    lookup_url_kwarg = "pk"
    queryset = Employee.objects.all()


class CandidateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrHrEmployee]
    model = CandidateInfo
    serializer_class = CandidateInfoSerializer
    lookup_url_kwarg = "pk"
    queryset = CandidateInfo.objects.prefetch_related(
        'skills', 'experiences'
    ).all()
    parser_classes = [MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'patch']

    def prepare_data(self, request_data):
        data = {key: request_data.get(key) for key in request_data.keys()}
        try:
            skills = json.loads(
                data.pop('skills')
            ) if 'skills' in data else []
            experience = json.loads(
                data.pop('experience')
            ) if 'experience' in data else []
        except JSONDecodeError as e:
            raise APIException(
                detail=f"Either skills or experience data is not correct. "
                       f"please correct and try again. "
                       f"HINT: skills is list of skill name, "
                       f"and experience is list of work experience objects."
            )
        if not skills and self.request.method in ['POST', 'PUT']:
            raise ValidationError(detail="'skills' are missing.")
        data.update(
            {
                'skills': skills,
                'experience': experience
            }
        )
        return data

    def process(self, kwargs, request, update=False):
        data = self.prepare_data(request.data)
        if update:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance=instance,
                data=data,
                partial=partial
            )
        else:
            serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if update:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request, *args, **kwargs):
        return self.process(kwargs, request)

    def update(self, request, *args, **kwargs):
        return self.process(kwargs, request, update=True)


class HRAssignInterviewApiView(CreateAPIView):
    permission_classes = [IsAdmin]
    http_method_names = ['post']
    serializer_class = HRAssignInterviewSerializer


class ActionAPIView(APIView):
    permission_classes = [IsHrEmployee]
    http_method_names = ['post']
    serializer_class = ActionSerializer

    def get_object(self):
        job_id = self.kwargs.get("job_id", None)
        obj = get_object_or_404(Interview, job_id=job_id)
        return obj

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.data.get("action", None)
        if not action:
            raise ValidationError("Action not provided.")
        valid_action, action_list = is_valid_action(action)
        if not valid_action:
            raise ValidationError(
                f"Invalid Action: Actions are as follows {', '.join(action_list)}"
            )
        obj = self.get_object()
        action_status, action_err = getattr(obj, f"action_{action}")()
        response_dict = {"status": action_status}
        if not action_status and action_err:
            response_dict.update({
                "errors": action_err
            })
        status_code = 200 if action_status else 400
        return Response(response_dict, status=status_code)


class InterviewRoundDetailAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewRoundSerializer
    queryset = InterviewRound.objects.all()

    def get_object(self):
        job_id = self.kwargs.get('job_id', None)
        round_no = self.kwargs.get('round_no', None)
        obj = get_object_or_404(
            InterviewRound,
            interview__job_id=job_id,
            round_no=round_no
        )
        return obj


class InterviewListRetrieveViewSet(
    ListModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAdminOrHrEmployee]
    serializer_class = InterviewSerializer
    queryset = Interview.objects.all()
    http_method_names = ['get']
    lookup_field = "job_id"

