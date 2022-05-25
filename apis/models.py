from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxValueValidator,
    FileExtensionValidator,
    RegexValidator
)
from django.db import models
from .selectors import (
    get_first_interview_round,
    check_candidate_failed_any_round,
    create_interview_round,
    get_interview_round,
    get_latest_interview_round
)
from .validators import validate_alphabets_only


User = get_user_model()


class Employee(User):  # Using Django Auth Model only, just using proxy model only.
    class Meta:
        proxy = True

    @property
    def role(self):
        emp_profile = self.emp_profile.first()
        if not emp_profile:
            return ""
        return emp_profile.role


class Role(models.TextChoices):
    HR = "HR"
    DEV = "DEV"


class EmployeeProfile(models.Model):
    user = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="emp_profile"
    )
    role = models.CharField(
        max_length=14,
        choices=Role.choices
    )

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        db_table = "employee_profile"

    def __str__(self):
        return f"{self.user} - {self.role}"


class Skill(models.Model):
    name = models.CharField(
        verbose_name="Skill Name",
        unique=True,
        max_length=80
    )

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        db_table = "skill"

    def __str__(self):
        return f"{self.name}"


class Gender(models.TextChoices):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class CandidateInfo(models.Model):
    email = models.EmailField(verbose_name="Email Address", max_length=120)
    first_name = models.CharField(
        verbose_name="First Name",
        max_length=70,
        validators=[validate_alphabets_only]
    )
    last_name = models.CharField(
        verbose_name="Last Name",
        max_length=50,
        validators=[validate_alphabets_only]
    )
    gender = models.CharField(
        verbose_name="Gender", choices=Gender.choices, max_length=6
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    mobile_no = models.CharField(
        validators=[phone_regex],
        max_length=13,
        null=True,
        blank=False
    )
    skills = models.ManyToManyField(to=Skill)
    resume = models.FileField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["doc", "docx", "pdf"]
            )
        ]
    )

    class Meta:
        verbose_name = "Candidate Information"
        verbose_name_plural = "Candidates Information"
        db_table = "candidate_info"

    def __str__(self):
        return f"{self.first_name} - {self.email}"


class WorkExperience(models.Model):
    candidate = models.ForeignKey(
        CandidateInfo,
        related_name="experiences",
        on_delete=models.CASCADE,
    )
    designation = models.CharField(
        max_length=50, verbose_name="Job Designation"
    )
    description = models.TextField(
        verbose_name="Job Description",
        null=True,
        blank=True,
    )
    total_experience = models.PositiveSmallIntegerField(
        verbose_name="Total Experience (in yrs.)",
        default=0,
        help_text="Total work experience in years"
    )

    class Meta:
        verbose_name = "Work Experience"
        verbose_name_plural = "Work Experience"
        db_table = "work_experience"

    def __str__(self):
        return f"{self.candidate}"


class InterviewStatus(models.TextChoices):
    SELECT = "SELECT"
    REJECT = "REJECT"


class Interview(models.Model):  # Sort of Interview history of candidate
    job_id = models.CharField(
        max_length=200,
        editable=False,
        null=True,
        blank=False
    )
    employee = models.ForeignKey(
        to=Employee,
        related_name="interviews",
        on_delete=models.CASCADE
    )
    candidate = models.ForeignKey(
        CandidateInfo,
        related_name="interviews",
        on_delete=models.CASCADE,
    )
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=6,
        choices=InterviewStatus.choices,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"
        db_table = "interview"

    def __str__(self):
        return f"{self.job_id}"

    # region Actions
    def action_start_first_round(self):
        err = []
        selected = InterviewStatus.SELECT.value
        rejected = InterviewStatus.REJECT.value
        if self.status == selected or self.status == rejected:
            err.append(f"Candidate status is already {self.status}, " 
                       "can't create first round")
        if get_first_interview_round(interview=self):
            err.append("First round already started")
        if err:
            return False, err
        create_interview_round(round_no=1, interview=self)
        return True, []

    def action_move_to_next_round(self, remarks=None):
        err = []
        selected = InterviewStatus.SELECT.value
        rejected = InterviewStatus.REJECT.value
        if self.status == selected or self.status == rejected:
            err.append(f"Invalid Action: Candidate status is already "
                       f"{self.status},can't move to next round")
        if not get_first_interview_round(interview=self):
            err.append("Invalid Action: First Round isn't started.")
        if check_candidate_failed_any_round(interview=self):
            err.append("Invalid Action: Candidate has failed one"
                       " of the round. can't move to next round")
        if err:
            return False, err
        round_list = list(InterviewRound.objects.filter(
            interview=self
        ).order_by(
            "round_no"
        ).values("round_no", "is_final_round"))
        final_round_vals = [
            val["is_final_round"] for val in round_list
            if "is_final_round" in val.keys()
        ]
        if final_round_vals and any(final_round_vals) is True:
            msg = f"Final Round is already taken for the no next round."
            return False, [msg]
        rounds = [
            val["round_no"] for val in round_list
            if "round_no" in val.keys()
        ]
        if not rounds:
            return False, ["Unexpected Error: No interview rounds found."]
        prev_round_no = rounds[-1]
        prev_round = get_interview_round(
            interview=self, round_no=prev_round_no
        )
        if not prev_round.status:
            prev_round.status = InterviewRoundStatus.PASS.value
            prev_round.remarks = remarks
            prev_round.save()
        next_round_no = prev_round_no + 1
        create_interview_round(round_no=next_round_no, interview=self)
        return True, []

    def action_reject(self, remarks=None):
        err = []
        if not get_first_interview_round(interview=self):
            err.append("Invalid Action: First Round isn't started.")
        if self.status == InterviewStatus.SELECT.value:
            # once a candidate is marked as selected
            # candidate cannot be rejected
            # (any updates to be done should be via admin)
            err.append("Invalid Action: Cannot mark reject, "
                       "candidate is already marked SELECT.")
        if err:
            return False, err
        self.status = InterviewStatus.REJECT.value
        self.save()
        InterviewRound.objects.filter(
            interview=self, status__isnull=True
        ).update(status=InterviewRoundStatus.FAIL.value, remarks=remarks)
        return True, []

    def action_select(self, remarks=None):
        err = []
        if not get_first_interview_round(interview=self):
            err.append("Invalid Action: First Round isn't started.")
        if self.status == InterviewStatus.REJECT.value:
            # once a candidate is marked as selected
            # candidate cannot be rejected
            # (any updates to be done should be via admin)
            err.append("Invalid Action: Cannot mark select, "
                       "candidate is already marked REJECT.")
        if check_candidate_failed_any_round(interview=self):
            err.append("Invalid Action: Candidate has failed one"
                       " of the round. can't move to next round")
        last_round = InterviewRound.objects.filter(
            interview=self, is_final_round=True
        ).order_by(
            "round_no"
        ).first()
        if not last_round:
            err.append("Invalid Action :Last round still pending"
                       " cannot proceed selection")
        if err:
            return False, err
        last_round.status = InterviewRoundStatus.PASS.value
        last_round.remarks = remarks
        last_round.save()
        if self.status == InterviewStatus.SELECT.value:
            return True, []
        self.status = InterviewStatus.SELECT.value
        self.save()
        return True, []

    def action_recommend(self, remarks=None):
        err = []
        selected = InterviewStatus.SELECT.value
        rejected = InterviewStatus.REJECT.value
        if self.status == selected or self.status == rejected:
            err.append(f"Invalid Action: Candidate status is already "
                       f"{self.status}")
        if not get_first_interview_round(interview=self):
            err.append("Invalid Action: First Round isn't started.")
        if check_candidate_failed_any_round(interview=self):
            err.append("Invalid Action: Candidate has failed one"
                       " of the round. can't recommend")
        if err:
            return False, err
        prev_round = get_latest_interview_round(interview=self)
        prev_round.status = InterviewRoundStatus.RECOMMEND.value
        prev_round.remarks = remarks
        prev_round.save()
        if prev_round.is_final_round is False:
            self.action_move_to_next_round()
        return True, []

    # endregion

    def generate_job_id(self):
        if not self.job_id:
            date_time = datetime.now().strftime("%d-%m-%Y")
            self.job_id = f"INT{date_time}-{self.pk}"

    def calculate_overall_rating(self):
        if self.status == InterviewStatus.SELECT.value:
            final_round_with_rating = self.interview_round.filter(
                is_final_round=True,
                rating__isnull=False
            ).exists()
            if final_round_with_rating:
                ratings = list(
                    self.interview_round.values_list("rating", flat=True)
                )
                overall_rating = round(sum(ratings)) / len(ratings)
                self.overall_rating = overall_rating

    def save(self, *args, **kwargs):
        self.generate_job_id()
        self.calculate_overall_rating()
        super().save(*args, **kwargs)


class InterviewRoundStatus(models.TextChoices):
    PASS = "PASS"
    FAIL = "FAIL"
    RECOMMEND = "RECOMMEND"


class InterviewRound(models.Model):
    interview = models.ForeignKey(
        related_name="interview_round",
        to=Interview,
        on_delete=models.CASCADE
    )
    round_no = models.PositiveSmallIntegerField(
        verbose_name="Round Number",
        null=True,
        blank=True
    )
    interviewer = models.ForeignKey(
        to=Employee,
        related_name="interview_rounds",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=9,
        choices=InterviewRoundStatus.choices,
        null=True,
        blank=True
    )
    remarks = models.TextField(null=True, blank=True)
    skills = models.ManyToManyField(to=Skill, blank=True)
    rating = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(10)]
    )
    date = models.DateField(
        verbose_name="Interview Round Date",
        blank=True,
        null=True
    )
    is_final_round = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Interview Round"
        verbose_name_plural = "Interview Rounds"
        db_table = "interview_round"

    def __str__(self):
        return f"{self.interview} - Round {self.round_no}"
