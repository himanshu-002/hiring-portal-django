from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from apis.models import (
    Skill,
    CandidateInfo,
    WorkExperience,
    User,
    EmployeeProfile,
    Employee,
    Interview,
    InterviewRound
)
from apis.utils import candidate_exists


class SkillAdmin(admin.ModelAdmin):
    pass


admin.site.register(Skill, SkillAdmin)


class WorkExperienceInline(admin.StackedInline):
    model = WorkExperience
    can_delete = True
    verbose_name = 'Past Work Experience'
    fk_name = 'candidate'
    extra = 0


class CandidateInfoAdminForm(forms.ModelForm):
    class Meta:
        model = CandidateInfo
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', None)
        if self.instance.pk:
            existing = candidate_exists(email, self.instance)
        else:
            existing = candidate_exists(email)
        if existing:
            raise forms.ValidationError(f"Candidate with email: {email}, already exists.")
        return cleaned_data


class CandidateInfoAdmin(admin.ModelAdmin):
    form = CandidateInfoAdminForm
    list_display = ['email', 'first_name', 'last_name', 'gender', 'mobile_no']
    inlines = [WorkExperienceInline]


admin.site.register(CandidateInfo, CandidateInfoAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = True
    verbose_name = 'Employee Profile'
    fk_name = 'user'
    extra = 1
    max_num = 1


class EmployeeAdmin(UserAdmin):
    inlines = [EmployeeProfileInline]
    list_display = UserAdmin.list_display + ("role",)


admin.site.register(Employee, EmployeeAdmin)


class InterviewAdminForm(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(
            emp_profile__role="HR"
        )
    )

    class Meta:
        model = Interview
        fields = '__all__'


class InterviewRoundInline(admin.StackedInline):
    model = InterviewRound
    can_delete = False
    verbose_name = 'Interview Round'
    fk_name = 'interview'
    extra = 0
    max_num = 0
    readonly_fields = ("round_no",)


class InterviewAdmin(admin.ModelAdmin):
    form = InterviewAdminForm
    inlines = [InterviewRoundInline]
    readonly_fields = ['job_id']


admin.site.register(Interview, InterviewAdmin)
