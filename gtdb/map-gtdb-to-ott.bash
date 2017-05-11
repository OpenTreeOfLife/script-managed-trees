#!/bin/bash
set -x
ref_seq_num="${1}"
ncbi_dir="${2}"
ott_dir="${3}"
if test -z "${ott_dir}" ; then
    echo "Expecting 3 arguments: a refseq number (no alphabetic characters), NCBI taxonomy in OTT interim taxonomy format, and OTT dir"
    exit 1
fi
# Verify inputs
inpdir="RefSeq${ref_seq_num}"
inprefix="${inpdir}/GTDB_RS${ref_seq_num}"
inmapping="${inprefix}.txt"
intre="${inprefix}.tre"
if ! test -d "${inpdir}" ; then
    echo "${inpdir} is not a directory"
    exit 1
elif ! test -f "${inmapping}" ; then
    echo "Missing mapping file at ${inmapping}"
    exit 1
elif ! test -f "${intre}" ; then
    echo "Missing tree file at ${intre}"
    exit 1
fi

cp "${ncbi_dir}/about.json" "${inpdir}/ncbi_about.json" || exit
cp "${ott_dir}/about.json" "${inpdir}/ott_about.json" || exit

outtoncbiid="${inpdir}/gtbd_id_to_ncbi_taxon_id.tsv"
errtoncbiid="${inpdir}/err-log-mapping-to-ncbi-id.txt"
if ! ./convert-mapping-file-to-ncbi-taxon-id.py "${inmapping}" "${ncbi_dir}" >"${outtoncbiid}" 2>"${errtoncbiid}" ; then
    echo "Mapping to NCBI IDs failed."
    exit 1
fi

outtoottid="${inpdir}/gtdb_id_to_ott_id.tsv"
errtoottid="${inpdir}/err-log-mapping-to-ott-id.txt"
if ! ./convert-ncbi-to-ott-id.py "${outtoncbiid}" "${ott_dir}" >"${outtoncbiid}" 2>"${errtoottid}" ; then
    echo "Mapping to OTT IDs failed."
    exit 1
fi

toidnewick="${inpdir}/gtdb_id_to_ott_id_newick.tsv"
if ! ./newick-convert-gtdb-names.py "${outtoottid}" >"${toidnewick}" ; then
    echo "Newick correcting mapping labels failed."
    exit 1
fi

outtree="${inpdir}/mapped_gtdb_rs${ref_seq_num}.tre"
errprune="${inpdir}/err-log-pruning.txt"
jprune="${inpdir}/pruning.json"
if ! otc-relabel-tree --remap "${toidnewick}" -j "${jprune}" "${intre}"  >"${outtree}" 2>"${errprune}" ; then
    echo "Mapping and pruning tree failed."
    exit 1
fi

echo "SUCCESS!"