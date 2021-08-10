import numpy as np
import pandas as pd
import sys


# INPUT ARGUMENTS ###############################

# Path to tab-delimited GWAS data file.
in_file = sys.argv[1]
# Gene of interest.
gene = sys.argv[2]
# Path where to write output to.
out_file = sys.argv[3]
# Path where to write simplified (dropping many columns) output to.
simplified_out_file = sys.argv[4]

################################################

df = pd.read_csv(in_file, sep='\t', dtype=str)


def is_gene_of_interest_affected(reported_genes_string):
    return gene in reported_genes_string.split(', ')


df['has_gene'] = df['REPORTED GENE(S)'].apply(lambda genes: is_gene_of_interest_affected(str(genes)))

df = df.loc[df['has_gene'] == True]
df = df.drop(['has_gene'], axis=1)

# Write out the filtered version of the input file containing just entries related to
# gene of interest.
df.to_csv(out_file, index=False)
print(f'Wrote {out_file}.')

# Write out simplified version of data with a subset of the columns.
df = df[['DISEASE/TRAIT', 'CHR_ID', 'CHR_POS', 'SNPS', 'CONTEXT']]
df.rename(columns={'DISEASE/TRAIT': 'condition', 'CHR_ID': 'chr', 'CHR_POS': 'start', 'SNPS': 'dbsnp_id', 'CONTEXT': 'variant_type'}, inplace=True)

df.to_csv(simplified_out_file, index=False)
print(f'Wrote {simplified_out_file}.')


