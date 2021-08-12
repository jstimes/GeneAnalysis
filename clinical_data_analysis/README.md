#### Datasources



* _TP53\_clinvar\_results.txt_- ClinVar data for TP53 acquired by selecting the download link on this URL: [https://www.ncbi.nlm.nih.gov/clinvar/?term=tp53%5Bgene%5D](https://www.ncbi.nlm.nih.gov/clinvar/?term=tp53%5Bgene%5D)
* _gwas_data_2021-07-08.tsv_ - from GWAS catalog downloads, v1.0: [https://www.ebi.ac.uk/gwas/docs/file-downloads](https://www.ebi.ac.uk/gwas/docs/file-downloads)

**ClinVar analysis**

Given a set of ClinVar results related to the TP53 gene, organizes the results by condition. Output file is a CSV with first column ‘condition’ and second column is a ‘;’-delimited list of dbSNP IDs associated with this condition.

Run with:

```
python3 analyze_clinvar.py data/TP53_clinvar_results.txt data/TP53_clinvar_reported_conditions.csv
```

This script generates a processed CSV file, _TP53_clinvar_reported_conditions.csv_, describing conditions associated with TP53 in ClinVar and the dbSNP IDs of variants associated with those conditions and TP53. The format is:

&lt;condition>,&lt;snp_id_1>;&lt;snp_id_2>;...

**GWAS Catalog analysis**

Given the entire GWAS dataset, filters the data to just entries where TP53 is one of the reported genes. The data can be downloaded from the link above; the original file is too large to be hosted. Ensure it’s in the ‘data/’ directory before running.

Run with:

```
python3 analyze_gwas.py data/gwas_data_2021-07-08.tsv data/TP53_gwas_data.csv data/TP53_simplified_gwas_data.csv
```

This script generates two output files, each containing data that pertains to the gene of interest, in this case, TP53. 



* _TP53_gwas_data.csv_ contains the same columns used in the input file, except rows are filtered such that only rows where TP53 is a related gene are included.
* _TP53\_simplified\_gwas\_data.csv_ drops most columns and renames others such that its contents are just the most relevant features and is more similar to output files from the _variant_analysis _pipeline described above.