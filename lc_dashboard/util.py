from typing import List
from dataclasses import dataclass


@dataclass
class UserScore:
    username: str
    rank: int
    score: int
    finish_time: float
    country_code: str
    passed_question_ids: List[str]


@dataclass
class ScorePage:
    competition_name: str
    questions: list
    submissions: list
    total_rank: list
    is_past: bool
    time: float
    user_num: int
    _questions_map = None

    @property
    def user_scores(self) -> List[UserScore]:
        users = []
        for user_submission, user_score in zip(self.submissions, self.total_rank):
            username, rank, score, finish_time, country_code = (
                user_score["username"],
                user_score["rank"],
                user_score["score"],
                user_score["finish_time"],
                user_score["country_code"],
            )
            users.append(
                UserScore(
                    username=username,
                    rank=rank,
                    score=score,
                    finish_time=finish_time,
                    country_code=country_code,
                    passed_question_ids=list(user_submission.keys()),
                )
            )
        return users

    @property
    def prepare_user_score_csv_logs(self) -> List[tuple]:
        logs = []
        for user_score in self.user_scores:
            # user_name, rank, percentile, score, finish_time, country_code, competition_name, passed_question_ids
            passed_question_ids_str = ",".join(user_score.passed_question_ids)
            log = (
                user_score.username,
                user_score.rank,
                user_score.rank / self.user_num,
                user_score.score,
                user_score.finish_time,
                user_score.country_code,
                self.competition_name,
                passed_question_ids_str,
            )
            logs.append(log)
        return logs
