import argparse
import os
import sys
import shutil

import pandas as pd

NANS = [
    "nan",
    "NA",
    "",
    " # N/A",
    "#N/A",
    "N/A",
    "#NA",
    "-1.#IND",
    "-1.#QNAN",
    "-NaN",
    "-nan",
    "1.#IND",
    "1.#QNAN",
    "<NA>",
    "N/A",
    "NA",
    "NULL",
    "NaN",
    "n/a",
    "nan",
    "null",
    "#DIV/0!",
    "unknown",
    "Unknown"
]

# kingdom: phyla[]
# Note that some phylum lists may contain non-phylum entries
# because I don't understand how these classifications work
# and also because too many is better than too few in this case
# so it should work out
KINGDOMS = {
    "Bacteria": [
        "Acidobacteria",
        "Actinobacteria",
        "Aquificae",
        "Armatimonadetes",
        "Bacteroidetes",
        "Caldiserica",
        "Chlamydiae",
        "Chlorobi",
        "Chloroflexi",
        "Chrysiogenetes",
        "Coprothermobacterota",
        "Cyanobacteria",
        "Deferribacteres",
        "Deinococcus-Thermus",
        "Dictyoglomi",
        "Elusimicrobia",
        "Fibrobacteres",
        "Firmicutes",
        "Fusobacteria",
        "Gemmatimonadetes",
        "Lentisphaerae",
        "Nitrospirae",
        "Planctomycetes",
        "Proteobacteria",
        "Spirochaetes",
        "Synergistetes",
        "Tenericutes",
        "Thermodesulfobacteria",
        "Thermotogae",
        "Verrucomicrobia"
    ],
    "Archaea": [
        "Euryarchaeota",  # Woese et al. 1990
        "Methanopyri",  # Garrity & Holt 2002
        "Methanococci",  # Boone 2002
        "Eurythermea",  # Cavalier-Smith 2002[2]
        "Neobacteria",  # Cavalier-Smith 2002[2]
        "DPANN",
        "ARMAN",
        "Micrarchaeota",  # Baker et al. 2010
        "Parvarchaeota",  # Rinke et al. 2013
        "Aenigmarchaeota",  # Rinke et al. 2013
        "Diapherotrites",  # Rinke et al. 2013
        "Nanoarchaeota",  # Huber et al. 2002
        "Nanohaloarchaeota",  # Rinke et al. 2013
        "Pacearchaeota",  # Castelle et al. 2015
        "Woesearchaeota",  # Castelle et al. 2015
        "Proteoarchaeota",  # Petitjean et al. 2015
        "TACK",
        "Filarchaeota",  # Cavalier-Smith, T. 2014[3]
        "Aigarchaeota",  # Nunoura et al. 2011
        "Bathyarchaeota",  # Meng et al. 2014
        "Crenarchaeota",  # Garrity & Holt 2002
        "Geoarchaeota",  # Kozubal et al. 2013
        "Korarchaeota",  # Barns et al. 1996
        "Thaumarchaeota",  # Brochier-Armanet et al. 2008
        "Asgardarchaeota",  # Violette Da Cunha et al., 2017
        "Lokiarchaeota",  # Spang et al. 2015
        "Thorarchaeota",  # Seitz et al. 2016
        "Odinarchaeota",  # Katarzyna Zaremba-Niedzwiedzka et al. 2017
        "Heimdallarchaeota",  # Katarzyna Zaremba-Niedzwiedzka et al. 2017
    ],
    "Protozoa": [
        "Euglenozoa",
        "Amoebozoa",
        "Metamonada",
        "Choanozoa",
        "Loukozoa",
        "Percolozoa",
        "Microsporidia",
        "Sulcozoa"
    ],
    "Chromista": [
        "Corbihelia",
        "Cryptophyta",
        "Centroheliozoa",
        "Haptophyta",
        "Filosa",
        "Retaria",
        "Ciliophora",
        "Miozoa",
        "Platysulcea",
        "Sagenista",
        "Placidozoa",
        "Bigyromonadea",
        "Peronosporomycota",
        "Hyphochytriomycota",
        "Pirsonea",
        "Ochrophyta"
    ],
    "Plantae": [
        "Chlorokybophyta",
        "Mesostigmatophyta",
        "Spirotaenia",
        "Chlorobionta",
        "Chlorophyta",
        "Streptobionta",
        "Klebsormidiophyceae",
        "Charophyta",
        "Chaetosphaeridiales",
        "Coleochaetophyta",
        "Zygnematophyta",
        "Embryophyta",
        "Marchantiophyta",
        "Bryophyta",
        "Anthocerotophyta",
        "Horneophyta",
        "Aglaophyta",
        "Tracheophyta"
    ],
    "Fungi": [
        "Rozellomyceta",
        "Rozellomycota",
        "Microsporidia",
        "Aphelidiomyceta",
        "Aphelidiomycota",
        "Eumycota",
        "Chytridiomyceta",
        "Neocallimastigomycota",
        "Chytridiomycota",
        "Blastocladiomyceta",
        "Blastocladiomycota",
        "Zoopagomyceta",
        "Basidiobolomycota",
        "Entomophthoromycota",
        "Kickxellomycota",
        "Mortierellomycota",
        "Mucoromyceta",
        "Calcarisporiellomycota",
        "Mucoromycota",
        "Symbiomycota",
        "Glomeromycota",
        "Entorrhizomycota",
        "Dikarya",
        "Basidiomycota",
        "Ascomycota"
    ],
    "Animalia": [
        "Acanthocephala",
        "Annelida",
        "Arthropoda",
        "Brachiopoda",
        "Bryozoa",
        "Chaetognatha",
        "Chordata",
        "Cnidaria",
        "Ctenophora",
        "Cycliophora",
        "Echinodermata",
        "Entoprocta",
        "Gastrotricha",
        "Gnathostomulida",
        "Hemichordata",
        "Kinorhyncha",
        "Loricifera",
        "Micrognathozoa",
        "Mollusca",
        "Nematoda",
        "Nematomorpha",
        "Nemertea",
        "Onychophora",
        "Orthonectida",
        "Phoronida",
        "Placozoa",
        "Platyhelminthes",
        "Porifera",
        "Priapulida",
        "Rhombozoa",
        "Rotifera",
        "Sipuncula",
        "Tardigrada",
        "Xenacoelomorpha"
    ]
}


def get_data(filename, excel_sheet=None):
    """
    Get raw data from a given filename.

    Args:
        parser (ArgumentParser): The argument parse for the program. Used for
            raising errors.
        filename (str): The file path/name.
        excel_sheet (str): The sheet name if using an excel_sheet sheet.
            Defaults to None.

    Returns:
        DataFrame: The extracted DataFrame.

    """
    # check if filename is string
    if type(filename) is not str:
        raise TypeError("filename is not string")

    # check if filename exists
    if not os.path.exists(filename):
        raise ValueError("file {} does not exist.".format(filename))

    # get raw data
    if (os.path.splitext(filename)[1]
        in [".xlsx", ".xlsm", ".xlsb",
            ".xltx", ".xltm", ".xls",
            ".xlt", ".xml"
            ]):  # using excel_sheet file
        if excel_sheet is not None:  # sheet given
            if excel_sheet.isdigit():  # sheet number
                raw_data = pd.read_excel(
                    filename,
                    sheet_name=int(excel_sheet) - 1,
                    na_values=NANS,
                    keep_default_na=True,
                    # engine="python"
                )
            else:  # sheet name
                raw_data = pd.read_excel(
                    filename,
                    sheet_name=excel_sheet,
                    na_values=NANS,
                    keep_default_na=True,
                    # engine="python"
                )
        else:  # sheet not given; use default first sheet
            raw_data = pd.read_excel(
                filename,
                sheet_name=0,
                na_values=NANS,
                keep_default_na=True,
                # engine="python"
            )

    elif ".csv" in os.path.splitext(filename)[1]:  # using csv
        raw_data = pd.read_csv(
            filename,
            na_values=NANS,
            keep_default_na=True,
            engine="python"
        )

    elif ".tsv" in os.path.splitext(filename)[1]:  # using tsv
        raw_data = pd.read_csv(
            filename,
            na_values=NANS,
            keep_default_na=True,
            sep="\t",
            engine="python"
        )

    # using txt; must figure out delimiter
    elif ".txt" in os.path.splitext(filename)[1]:
        raw_data = pd.read_csv(
            filename,
            na_values=NANS,
            keep_default_na=True,
            sep=None,
            engine="python"
        )
    else:  # invalid extension
        raise TypeError(
            "data file type is unsupported, or file extension not included")

    return raw_data  # return extracted data


def write_fasta(data, filename):
    """
    Write a fasta file from a dataframe of sequence data.

    Args:
        data (DataFrame): sequence data, preferably filtered.
        filename (str): path to save fasta file to.
    """
    with open(filename, "w") as file:
        for index, row in data.iterrows():
            file.write(">{}\n".format(row["sampleid"]))  # bin_uri -> sampleid
            file.write(row["nucleotides"])
            file.write("\n")


def filter_data(data):
    # change to str in case it's not
    data["nucleotides"] = data["nucleotides"].astype(str)

    # remove rows missing COI-5P in marker_codes (if column provided)
    if "marker_codes" in data.columns:
        # avoid exceptions by casting to str
        data["marker_codes"] = data["marker_codes"].astype(str)
        data = data[data["marker_codes"].str.contains("COI-5P", na=False)]

    # drop legitimate duplicate rows (changed to remove extraneous warning)
    data = data.drop_duplicates()

    # drop cases where there is only one sample for a given bin_uri
    # data = data.groupby("bin_uri").filter(lambda x: len(x) > 1)
    # ^ NOT USED

    # remove rows where sequence contains characters outside allowable set
    # regex [^ACGTURYKMSWBDHVN] matches all characters which are not in set
    data = data[data["nucleotides"].str.contains(
        "[^ACGTURYKMSWBDHVN]", regex=True) == False]

    # replace NA values with empty string for formatting of output files
    data.fillna('', inplace=True)

    return data.reset_index()


def get_kingdom(row):
    kingdom = [
        king for king
        in KINGDOMS
        if row["phylum_name"] in KINGDOMS[king]
    ]

    if len(kingdom) != 1:
        return ""
    else:
        return kingdom[0]


def main():

    parser = argparse.ArgumentParser(
        description="Convert BOLD-style data to files useable by QIIME2")

    parser.add_argument("input_file", help="File to convert")
    parser.add_argument(
        "-k",
        "--kingdom",
        help="Override kingdom for all samples with given argument",
        default=None
    )
    parser.add_argument(
        "-e",
        "--excel-sheet",
        help="Specify the excel sheet name or number",
        default=None,
        dest="sheet"
    )
    parser.add_argument(
        "output_name", help="Output folder name and filename prefix")
    args = parser.parse_args()

    data = None
    try:
        data = get_data(args.input_file, args.sheet)
    except ValueError:
        print("ERROR: Input file not found.")
    except TypeError:
        print("ERROR: Input type not supported.")

    if data is None:
        exit(-1)

    data = filter_data(data)

    # make output directory
    if os.path.isdir(args.output_name):
        resp = input(
            "The provided output name already exists as a folder. Overwrite? (y/n)\n> ")
        while resp not in ("y", "n"):
            resp = input("please input y (yes) or n (no)\n> ")
        if resp == "n":
            print("Please re-run the program with a new output name.")
            exit(1)
        else:
            shutil.rmtree(args.output_name)

    os.mkdir(args.output_name)

    fname_prefix = os.path.split(args.output_name)[-1]

    # write fasta file
    write_fasta(data, os.path.join(
        args.output_name,
        "{}_fasta.fasta".format(fname_prefix)
    ))

    def make_taxonomy_row(row):
        return "k__{}; p__{}; c__{}; o__{}; f__{}; g__{}; s__{}".format(
            args.kingdom if args.kingdom != None else get_kingdom(row),
            row["phylum_name"],
            row["class_name"],
            row["order_name"],
            row["family_name"],
            row["genus_name"],
            row["species_name"]
        )

    # make the second file
    taxonomy = pd.concat(
        [
            data["sampleid"],  # bin_uri -> sampleid
            data.apply(lambda row: make_taxonomy_row(row), axis=1)
        ],
        axis=1
    )

    taxonomy.to_csv(
        os.path.join(args.output_name, fname_prefix + "_taxonomy.tsv"),
        sep="\t",
        header=["sampleid", "taxonomy"],  # bin_uri -> sampleid
        index=False
    )

    otu_sid_map = data[["sampleid", "bin_uri"]]

    otu_sid_map.to_csv(
        os.path.join(args.output_name, fname_prefix + "_sampleid_map.tsv"),
        sep="\t",
        index=False
    )


if __name__ == '__main__':
    main()
