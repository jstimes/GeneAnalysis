import numpy as np
import pandas as pd
import sys


in_file = sys.argv[1]
out_file = sys.argv[2]

CONDITION_DELIM = '|'

DISCARDED_CONDITIONS = [
    'none provided',
    'none specified',
    'not specified',
    'not provided',
    'See cases',
]

df = pd.read_csv(in_file, sep='\t')

condition_to_snps = {}
for _, row in df.iterrows():
    db_snp_id = str(row['dbSNP ID'])
    conditions_packed = row['Condition(s)']
    conditions = conditions_packed.split("|")
    for condition in conditions:
        if condition in DISCARDED_CONDITIONS:
            continue
        if condition not in condition_to_snps:
            condition_to_snps[condition] = set()
        if db_snp_id != 'nan':
            condition_to_snps[condition].add(db_snp_id)

with open(out_file, 'w') as output:
    for condition, snps in condition_to_snps.items():
        output.write(f'{condition},' + ';'.join(snps) + '\n')
print(f'Wrote {out_file}.')

