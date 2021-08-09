# Given a genome annotation file and a gene ID, extracts the annotations 
# containing the gene. Writes an annotation file for just the gene,
# and generates bed files for the whole gene and for just exons.

import pandas as pd
import sys

# Turn off warning for false positive for setting values on copy df.
pd.options.mode.chained_assignment = None

# INPUT ARGUMENTS ######################################################

# .gff3 annotation file.
ANNOTATION_FILE = sys.argv[1]
# Gene of interest
GENE_ID = sys.argv[2]
# Prefix to be used for output files.
OUTPUT_PATH_PREFIX = sys.argv[3]

########################################################################

GFF3_COLUMNS = [
    'seqid',
    'source',
    'type',
    'start',
    'end',
    'score',
    'strand',
    'phase',
    'attributes',
]

annotation_output_file = f'{OUTPUT_PATH_PREFIX}{GENE_ID}.gff3'
bed_output_file = f'{OUTPUT_PATH_PREFIX}{GENE_ID}.bed'
exons_output_file = f'{OUTPUT_PATH_PREFIX}{GENE_ID}_exons.bed'
in_file = open(ANNOTATION_FILE, 'r')
out_file = open(annotation_output_file, 'w')

for line in in_file.readlines():
    key = f'gene_name={GENE_ID};'
    if key in line:
        out_file.write(line + '\n')

in_file.close()
out_file.close()
print(f'Wrote {annotation_output_file}.')

df = pd.read_csv(annotation_output_file, delimiter='\t', names=GFF3_COLUMNS)
bed_df = df[['type', 'seqid', 'start', 'end', 'attributes', 'strand']]
bed_df['dot'] = '.'
bed_df.loc[bed_df['type'] == 'gene'].to_csv(bed_output_file, 
        sep='\t', 
        columns=['seqid', 'start', 'end', 'attributes', 'dot', 'strand'], 
        header=False, 
        index=False)
print(f'Wrote {bed_output_file}.')

bed_df.loc[bed_df['type'] == 'exon'].to_csv(exons_output_file, 
        sep='\t', 
        columns=['seqid', 'start', 'end', 'attributes', 'dot', 'strand'], 
        header=False, 
        index=False)
print(f'Wrote {exons_output_file}.')

