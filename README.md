# lc-dashboard

## start service 

```
docker compose up
```


## data source from google sheet with following cols

example sheet: https://docs.google.com/spreadsheets/d/1wADT0jfyHTXAcu5WK3Sa3KGKWaoCwcFZ_sCQqR2XZrY/edit#gid=0

score sheet with 
```csv
name	rank	percentile	score	ts	country	competition passed_questions(split via ,)
nekosyndrome	80	0.003477353734	19	1686453148	TW	weekly-contest-349	2810,2828,2836,2839
```

second sheet with question tag (set env gid withQUESTION_TAG_GID)
```csv
question_id	credit	title	title-slug	competition	tag1	tag2	level
2839	7	maximum sum queries	maximum-sum-queries	weekly-contest-349	Heap		Hard
```


the script used to dump data is in lc_dashboard/scripts/prepare_*.py



## service deployed with streamlit

https://lc-dashboard-4bycchs3trns2gwnyfappvw.streamlit.app/know-your-self

if you wanna having your own change, feel free to sent me pr / fork it 
and deploy your own [streamlit deploy tutorial].(https://docs.streamlit.io/streamlit-community-cloud/get-started)