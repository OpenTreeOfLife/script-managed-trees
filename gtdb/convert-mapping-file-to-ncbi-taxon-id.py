#!/usr/bin/env python
import codecs
import sys
import os
script_name = os.path.split(sys.argv[0])[-1]
def debug(m):
    sys.stderr.write("{}: {}\n".format(script_name, m))

try:
    mapping_file = sys.argv[1]
    ncbi_taxonomy_dir = sys.argv[2]
    assert os.path.isfile(mapping_file)
    assert os.path.isdir(ncbi_taxonomy_dir)
except:
    raise
    sys.exit("Expecting 2 arguments: the mapping file from GTDB ID to NCBI name and a directory that holds a NCBI taxonomy in Open Tree Interim Taxonomy format")
with codecs.open(mapping_file, 'rU', encoding='utf-8') as minp:
    gtdbid_to_name = {}
    name_to_gtdbids = {}
    for line in minp:
        ls = line.strip()
        if not ls:
            continue
        try:
            gtdbid, name = [i.strip() for i in ls.split('\t')]
        except:
            sys.exit("Expecting 1 tab in a  non-empty line. Found:\n{}".format(line))
        gtdbid_to_name[gtdbid] = name
        name_to_gtdbids.setdefault(name, []).append(gtdbid)
    debug("{} NCBI names, {} gtdbids".format(len(name_to_gtdbids), len(gtdbid_to_name)))

ncbi_name_to_ncbi_tax_id_set = {}

taxonomy_tsv = os.path.join(ncbi_taxonomy_dir, 'taxonomy.tsv')
with codecs.open(taxonomy_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        name = ls[2]
        if name in name_to_gtdbids:
            uid = ls[0]
            ncbi_name_to_ncbi_tax_id_set.setdefault(name, set()).add(uid)
num_found_in_taxonomy = len(ncbi_name_to_ncbi_tax_id_set)
debug("{} NCBI names found in {}".format(num_found_in_taxonomy, taxonomy_tsv))

synonyms_tsv = os.path.join(ncbi_taxonomy_dir, 'synonyms.tsv')
with codecs.open(synonyms_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        name = ls[1]
        if name in name_to_gtdbids:
            uid = ls[0]
            ncbi_name_to_ncbi_tax_id_set.setdefault(name, set()).add(uid)
num_found_in_ncbi = len(ncbi_name_to_ncbi_tax_id_set)
num_found_in_synonyms = num_found_in_ncbi - num_found_in_taxonomy
debug("{} NCBI names found in {}".format(num_found_in_synonyms, synonyms_tsv))

gtdbid_to_ncbi_taxon_id = {}
amig = set()
for name, ntset in ncbi_name_to_ncbi_tax_id_set.items():
    gtdb_ids = name_to_gtdbids[name]
    if len(ntset) > 1:
        debug("Dropping GTDB Ids {} ambiguously map to multiple NCBI IDs: {}".format(gtdb_ids, list(ntset)))
    else:
        assert len(ntset) == 1
        ntid = list(ntset)[0]
        for gtdb_id in gtdb_ids:
            gtdbid_to_ncbi_taxon_id[gtdb_id] = ntid
debug("{} GTDB IDs mapped unambiguously to an NCBI taxon ID".format(len(gtdbid_to_ncbi_taxon_id)))
out = sys.stdout
klist = list(gtdbid_to_ncbi_taxon_id)
klist.sort()

for k in klist:
    out.write('{}\t{}\n'.format(k, gtdbid_to_ncbi_taxon_id[k]))

