# Adds dbSnp ID to info string so it can be included in bed file.

import sys

# INPUT ARGUMENTS ####################################################

# Input vcf file.
vcf_file = sys.argv[1]
# Output file name
out_file_name = sys.argv[2]

#####################################################################


in_file = open(vcf_file, 'r')
out_file = open(out_file_name, 'w')

for line in in_file.readlines():
    parts = line.split('\t')
    if len(parts) != 8:
        continue
    parts[7] = parts[7].replace('\n', '')
    parts[7] = parts[7] + ';dbSnpRef=' + parts[2]
    out_file.write('\t'.join(parts) + '\n')

in_file.close()
out_file.close()
print(f"Wrote {out_file_name}.")

