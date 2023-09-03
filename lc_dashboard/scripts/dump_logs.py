import time
import requests
logs = []
contests = [f'weekly-contest-{i}' for i in range(349, 362)] + [f'biweekly-contest-{i}' for i in range(106, 113)]

for test in contests:
    for i in range(1, 201):
        res = requests.get(f"https://leetcode.com/contest/api/ranking/{test}/?pagination={i}&region=global")
        res_dict = res.json()
        time.sleep(0.0025)
        for user in res_dict['total_rank']:
            if user['country_code'] == 'TW':
                logs.append((user['username'], user['rank'], user['rank'] / res_dict['user_num'],user['score'], user['finish_time'], user['country_code'], test))
    print(test, len(logs))