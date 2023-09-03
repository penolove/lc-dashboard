# lc-dashboard

## start service 

```
docker compose up
```


## data source from google sheet with following cols

example sheet: https://docs.google.com/spreadsheets/d/1wADT0jfyHTXAcu5WK3Sa3KGKWaoCwcFZ_sCQqR2XZrY/edit#gid=0

```
name	rank	percentile	score	ts	country	competition
```

the script used to dump data is in lc_dashboard/scripts/dump_logs.py
