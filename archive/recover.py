import re
import json
import pandas as pd

log_path = r'c:\Users\hp\.gemini\antigravity-ide\brain\35014449-b937-456a-baca-c96c1476018e\.system_generated\tasks\task-123.log'
with open(log_path, 'r', encoding='utf-8') as f:
    log = f.read()

names = re.findall(r'\[\d+/27\] (.*?)\n', log)
cites = re.findall(r'\(Cites: (.*?), H: (.*?)\)', log)
found_statuses = re.findall(r'Finding profile URL for \'.*?\'... (.*?)\n', log)

c_idx = 0
records = []
for n, f_status in zip(names, found_statuses):
    rec = {'Name': n, 'Department': 'Chemistry'}
    if 'Found' in f_status:
        rec['Citations_All'] = cites[c_idx][0]
        rec['H_Index_All'] = cites[c_idx][1]
        c_idx += 1
    else:
        rec['Citations_All'] = 'N/A'
        rec['H_Index_All'] = 'N/A'
    records.append(rec)

df = pd.DataFrame(records)
df.to_csv('baseline.csv', index=False)
print(f"Recovered baseline.csv with {len(df)} records.")
