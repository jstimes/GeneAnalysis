# This script does the following:
# a) Parses a given variant bed file
# b) Looks up variants specified in that file in dbsnp.
# c) Combines the bed file and dbsnp data.
# d) Writes this data to a new CSV file.
# e) Generates distributions of:
#    1) Variant type distribution,
#    2) Allele frequency distribution.
# f) Generates a txt report with high-level data about the variants.

from dbsnp_api import get_refsnps
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import re
import requests
import sys
import time


# INPUT ARGUMENTS ######################################################

# Specifies location of variants bed file to read.
variant_file_path = sys.argv[1]
# Specifies prefix of output files generated by this script.
output_file_prefix = sys.argv[2]

########################################################################

SUBCOL_DELIM = ";"


# Extracts a certain piece of info from the ;-delimited info column
def get_field_with_prefix(fields, prefix):
    field = next(field for field in fields if field.find(prefix) == 0)
    return field[len(prefix):]


# Given a list with objects of varying type (e.g. str, num, etc), removes
# nans.
def drop_nans(mixed_objects_list):
    return list(filter(lambda x: x == x, mixed_objects_list))


# Given a list containing delimited-strings, returns a new list containing
# all split strings (e.g. unpack(['a;b;c']) -> ['a', 'b', 'c'].
def unpack(in_list):
    out_list = []
    for item in in_list:
        items = item.split(SUBCOL_DELIM)
        out_list = out_list + items
    return out_list


# Reads and returns the data in the gene variant's bed file
def parse_gene_variants(file_path):
    dataframe_data = []
    with open(file_path, 'r') as f:
        for line in f.readlines():
            data = {}
            fields = line.split('\t')
            data['chr'] = fields[0]
            data['start'] = fields[1]
            data['stop'] = fields[2]
            info_field = fields[3]
            info_subfields = info_field.split(';')
            af = float(get_field_with_prefix(info_subfields, 'AF='))
            data['allele_frequency'] = af
            vt = get_field_with_prefix(info_subfields, 'VT=')
            data['variant_type'] = vt
            dbsnp = get_field_with_prefix(info_subfields, 'dbSnpRef=')
            data['dbsnp_id'] = dbsnp
            dataframe_data.append(data)
    return dataframe_data


# Saves a currently plotted histogram with the given metadata.
def save_hist(xlabel=None, ylabel=None, title=None, filename=None):
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(filename)
    plt.clf()
    print(f'Generated {filename}.')


# Generates a variant summary report given a DataFrame.
def generate_report(df):
    total_variants = len(df)
    all_variant_types = df['variant_type'].unique()
    all_dbsnp_variant_types = drop_nans(df['dbsnp_variant_type'].unique())
    all_diseases = set(unpack(drop_nans(df['diseases'].unique())))
    significances = set(unpack(drop_nans(df['significances'].unique())))
    origins = set(unpack(drop_nans(df['origins'].unique())))
    max_allele_frequency = df['allele_frequency'].max()
    avg_allele_frequency = df['allele_frequency'].mean()

    output_report_file = f'{output_file_prefix}_report.txt'
    with open(output_report_file, 'w') as out:
        out.write(f'Total variants: {total_variants}.\n')
        out.write(f'Variant types present: ' + ', '.join([str(vt) for vt in all_variant_types]) + '.\n')
        out.write(f'dbSnp variant types present: ' + ', '.join([str(vt) for vt in all_dbsnp_variant_types]) + '.\n')
        out.write(f'Max allele frequency: {max_allele_frequency}.\n')
        out.write(f'Avg allele frequency: {avg_allele_frequency}.\n')
        out.write(f'Diseases: {all_diseases}.\n')
        out.write(f'Significances: {significances}.\n')
        out.write(f'Origins: {origins}.\n')

    print(f'Wrote {output_report_file}.')


# Runs all analyses to generate a new data sheet, plots, and a report.
def main():
    df = pd.DataFrame(parse_gene_variants(variant_file_path))
    dbsnp_data = get_refsnps(df['dbsnp_id'].unique())
    dbsnp_df = pd.DataFrame(dbsnp_data)
    df = df.merge(dbsnp_df, how='left', on='dbsnp_id')
    
    df['variant_type'].hist()
    save_hist(xlabel='variant type', 
              ylabel='# Variants', 
              title='Variant type distribution', 
              filename=f'{output_file_prefix}_variant_type_distribution.png')

    df['allele_frequency'].hist()
    save_hist(xlabel='allele frequency',
              ylabel='# alleles',
              title='Distribution of allele frequencies',
              filename=f'{output_file_prefix}_af_distribution.png')

    generate_report(df)

    output_data_file = f'{output_file_prefix}.csv'
    df.to_csv(output_data_file, index=False)
    print(f'Wrote {output_data_file}.')


main()

