import time
import requests
import pandas as pd

from lc_dashboard.util import ScorePage

logs = []
contests = [f'weekly-contest-{i}' for i in range(349, 362)] + [f'biweekly-contest-{i}' for i in range(106, 113)]

for test in contests:
    res = requests.get(f"https://leetcode.com/contest/api/ranking/{test}/?pagination=1&region=global")
    
    res_dict = res.json()
    time.sleep(0.0025)
    score_page = ScorePage(**res_dict, competition_name=test)
    
    df = pd.DataFrame(score_page.questions)[['question_id', 'credit', 'title', 'title_slug']]
    df['contest'] = test
    logs.extend(df.values.tolist())