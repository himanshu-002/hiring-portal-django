from rest_framework.exceptions import ValidationError
from apis.models import CandidateInfo, Employee, Role, Interview, Skill


def candidate_exists(email, instance=None):
    existing_candidate = CandidateInfo.objects.filter(email=email).first()
    if not existing_candidate:
        return False
    if instance:
        if instance.pk != existing_candidate.pk:
            return True
        else:
            return False
    return True


def is_hr_employee(employee: Employee):
    return bool(employee.role == Role.HR.value)


def is_valid_action(action):
    action_list = [
        act.replace("action_", "") for act in dir(Interview)
        if act.startswith("action")
    ]
    if action.lower() in action_list:
        return True
    return False


def validate_skills(instance, attrs, skills):
    if not skills and not instance:
        raise ValidationError(
            {"detail": "'skills' is a required field."}
        )
    if skills:
        all_skills = list(Skill.objects.values_list('name', flat=True))
        missing_skills = []
        for skill in skills:
            if skill['name'] not in all_skills:
                missing_skills.append(skill)
        if missing_skills:
            raise ValidationError(
                {"detail":
                    f"{', '.join(missing_skills)} are not valid 'skills'. "
                    f"valid choices are: {', '.join(all_skills)}"}
            )
        skills_list = list(Skill.objects.filter(
            name__in=[skill['name'] for skill in skills]
        ).values_list("id", flat=True))
        attrs.update({
            'skills': skills_list,
        })
        return attrs
