from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, APIException

from apis.models import (
    Skill,
    Employee,
    CandidateInfo,
    WorkExperience, Interview, InterviewRound,
)
from apis.utils import candidate_exists, is_hr_employee, validate_skills


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = (
            'name',
        )


class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(required=True)

    class Meta:
        model = Employee
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_active',
            'role'
        )
        read_only_fields = ('id',)

    def validate_role(self, role):
        choices = ['HR', 'DEV']
        if not role or role not in choices:
            raise ValidationError(
                detail=f"please provide valid value for role\
                 choices are : {', '.join(choices)}"
            )
        return role

    @transaction.atomic()
    def create(self, validated_data):
        role = validated_data.pop('role', None)
        try:
            emp = super().create(validated_data)
        except Exception as e:
            return APIException(
                detail=f"Employee not created, error: {e.__str__()}"
            )
        emp.emp_profile.create(role=role)
        return emp

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        emp_profile = instance.emp_profile.first()
        if emp_profile:
            emp_profile.role = role
            emp_profile.save(update_fields=['role'])
        else:
            instance.emp_profile.create(role=role)
        return super().update(instance, validated_data)


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = (
            'id',
            'designation',
            'description',
            'total_experience'
        )


class SkillListSerializer(SkillSerializer):
    def to_representation(self, instance):
        return instance.name


class CandidateInfoSerializer(serializers.ModelSerializer):
    skills = SkillListSerializer(many=True, read_only=True)
    experience = WorkExperienceSerializer(
        source='experiences', many=True, read_only=True
    )

    class Meta:
        model = CandidateInfo
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'mobile_no',
            'gender',
            'skills',
            'resume',
            'experience'
        )
        read_only_fields = ('id',)

    def validate_email(self, email):
        if self.instance:
            existing = candidate_exists(email, self.instance)
        else:
            existing = candidate_exists(email)
        if existing:
            raise ValidationError(
                detail=f"Candidate with email: {email}, already exists."
            )
        return email

    def validate(self, attrs):
        experience = self.initial_data.get('experience', [])
        if experience:
            exp_serializer = WorkExperienceSerializer(
                data=experience, many=True
            )
            try:
                exp_serializer.is_valid(raise_exception=True)
            except Exception as e:
                raise ValidationError(detail=f"'experience' : {e.__str__()}")
            attrs.update({
                'experience': experience,
            })
        skills = self.initial_data.get('skills', [])
        validate_skills(self.instance, attrs, skills)
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        experiences = validated_data.pop('experience', [])
        try:
            candidate = super().create(validated_data)
            for experience in experiences:
                WorkExperience.objects.create(candidate=candidate, **experience)
        except Exception as e:
            raise APIException(
                detail=f"Candidate not created, error: {e.__str__()}"
            )
        return candidate

    @transaction.atomic()
    def update(self, instance, validated_data):
        experiences = validated_data.pop('experience', [])
        try:
            instance = super().update(instance, validated_data)
            for experience in experiences:
                if "id" not in experience.keys():
                    WorkExperience.objects.create(
                        candidate=instance, **experience
                    )
                else:
                    exp_id = experience.pop("id")
                    exp_obj = WorkExperience.objects.get(
                        candidate=instance, id=exp_id
                    )
                    for field, value in experience.items():
                        setattr(exp_obj, field, value)
                    exp_obj.save()
        except Exception as e:
            raise APIException(
                detail=f"Candidate not updated, error: {e.__str__()}"
            )
        return instance


class HRAssignInterviewSerializer(serializers.ModelSerializer):
    employee = serializers.CharField()
    candidate = serializers.CharField()

    class Meta:
        model = Interview
        fields = (
            "employee",
            "candidate"
        )

    @staticmethod
    def get_custom_lookup(value, lookup_key):
        """
        Does a custom lookup can accept email or id as
        identifier for the fetching object on validation.
        """
        if value.isnumeric():
            lookup_key = "id"
        lookup = {lookup_key: value}
        return lookup

    def validate_employee(self, employee):
        lookup = self.get_custom_lookup(employee, "username")
        try:
            employee = Employee.objects.get(**lookup)
        except ObjectDoesNotExist:
            raise ValidationError(detail="Employee not Found.")
        if not is_hr_employee(employee):
            raise ValidationError(
                detail="Assigned Employee must be a HR. \
                       please check Employee is assigned any role"
            )
        return employee

    def validate_candidate(self, candidate):
        lookup = self.get_custom_lookup(candidate, "email")
        try:
            candidate = CandidateInfo.objects.get(**lookup)
        except ObjectDoesNotExist:
            raise ValidationError(detail="Candidate not Found.")
        return candidate


class ActionSerializer(serializers.Serializer):
    action = serializers.CharField()


class InterviewRoundSerializer(serializers.ModelSerializer):
    skills = SkillListSerializer(many=True, read_only=True)
    interviewer = serializers.CharField(
        source="interviewer.username",
        read_only=True
    )
    date = serializers.DateField(
        format="%d-%m-%Y",
        input_formats=["%d-%m-%Y"]
    )
    interview = serializers.StringRelatedField()

    class Meta:
        model = InterviewRound
        fields = (
            "id",
            "round_no",
            "interview",
            "interviewer",
            "status",
            "rating",
            "remarks",
            "skills",
            "date",
            "is_final_round"
        )
        read_only_fields = (
            "id",
            "interview",
            "status",
        )

    def validate(self, attrs):
        skills = self.initial_data.get('skills', [])
        validate_skills(self.instance, attrs, skills)
        interviewer = self.initial_data.get('interviewer', None)
        if not self.instance and not interviewer:
            raise ValidationError(detail="interviewer is a required field.")
        interviewer_obj = Employee.objects.filter(
            username=interviewer
        ).first()
        if not interviewer_obj:
            raise ValidationError(detail="Employee(Interviewer) not Found.")
        attrs.update({"interviewer": interviewer_obj})
        return attrs


class InterviewSerializer(serializers.ModelSerializer):
    interview_rounds = InterviewRoundSerializer(
        source="interview_round", many=True, read_only=True
    )
    employee = serializers.CharField(source="employee.username")
    candidate = serializers.CharField(source="candidate.email")

    class Meta:
        model = Interview
        fields = (
            "id",
            "job_id",
            "employee",
            "candidate",
            "status",
            "overall_rating",
            "interview_rounds"
        )
