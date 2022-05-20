from apis import models


def get_interview_round(interview, round_no):
    return models.InterviewRound.objects.filter(
        round_no=round_no,
        interview=interview
    ).first()


def get_first_interview_round(interview):
    return get_interview_round(interview, round_no=1)


def check_candidate_failed_any_round(interview):
    return models.InterviewRound.objects.filter(
        interview=interview,
        status=models.InterviewRoundStatus.FAIL.value
    ).exists()


def create_interview_round(round_no, interview):
    models.InterviewRound.objects.create(
        round_no=round_no, interview=interview
    )



