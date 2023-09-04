import time
import requests

from lc_dashboard.util import ScorePage

logs = []
contests = [f'weekly-contest-{i}' for i in range(349, 362)] + [f'biweekly-contest-{i}' for i in range(106, 113)]

for test in contests:
    for i in range(1, 201):
        res = requests.get(f"https://leetcode.com/contest/api/ranking/{test}/?pagination={i}&region=global")
        res_dict = res.json()
        time.sleep(0.0025)
        score_page = ScorePage(**res_dict, competition_name=test)
        for log in score_page.prepare_user_score_csv_logs:
            if log[-3] == 'TW':
                logs.append(log)