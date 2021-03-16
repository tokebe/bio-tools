# bio-tools

 A collection of small, single-purpose tools for bioinformatics.

## Contents

### bold2qiime

A command-line script for converting [BOLD](http://www.barcodinglife.org/)-formatted data downloads into [QIIME 2](https://qiime2.org/)-ready unaligned fasta and taxonomy files for q2-feature-classifer use.

Currently extracts COI-5P sequences and infers kingdom before formatting. Supports any plain-text regularly delimited file, as well as multi-sheet excel files, as input.

Usage: `bold2qiime.py -h`
