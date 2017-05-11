#!/usr/bin/env python
import codecs
import sys
import os
script_name = os.path.split(sys.argv[0])[-1]
def debug(m):
    sys.stderr.write("{}: {}\n".format(script_name, m))

try:
    to_ncbi_mapping_file = sys.argv[1]
    ott_dir = sys.argv[2]
    assert os.path.isfile(to_ncbi_mapping_file)
    assert os.path.isdir(ott_dir)
except:
    raise
    sys.exit("Expecting 2 arguments: the mapping file from GTDB ID to NCBI ID and a directory for OTT")
with codecs.open(to_ncbi_mapping_file, 'rU', encoding='utf-8') as minp:
    gtdbid_to_ncbi_taxon_id = {}
    ncbi_id_to_gtdbid_list = {}
    for line in minp:
        ls = line.strip()
        if not ls:
            continue
        try:
            gtdbid, ncbi_taxon_id = [i.strip() for i in ls.split('\t')]
        except:
            sys.exit("Expecting 1 tab in a  non-empty line. Found:\n{}".format(line))
        gtdbid_to_ncbi_taxon_id[gtdbid] = ncbi_taxon_id
        ncbi_id_to_gtdbid_list.setdefault(ncbi_taxon_id, []).append(gtdbid)
    debug("{} NCBI IDs, {} gtdb IDs".format(len(ncbi_id_to_gtdbid_list), len(gtdbid_to_ncbi_taxon_id)))

ncbi_id_to_ott_id = {}
ott_id_seen = set()
def process_ott_src_info(src_info, ott_id):
    src_list = src_info.split(',')
    for s in src_list:
        if s.startswith('ncbi:'):
            ncbi_id = s[5:]
            if ncbi_id in ncbi_id_to_gtdbid_list:
                ncbi_id_to_ott_id.setdefault(ncbi_id, set()).add(ott_id)
                ott_id_seen.add(ott_id)


taxonomy_tsv = os.path.join(ott_dir, 'taxonomy.tsv')
with codecs.open(taxonomy_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        src = ls[4]
        if 'ncbi:' in src:
            process_ott_src_info(src, ls[0])

num_found_in_taxonomy = len(ncbi_id_to_ott_id)
debug("{} NCBI IDs found in {}".format(num_found_in_taxonomy, taxonomy_tsv))

synonyms_tsv = os.path.join(ott_dir, 'synonyms.tsv')
with codecs.open(synonyms_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        src = ls[4]
        if 'ncbi' in src:
            process_ott_src_info(src, ls[1])

num_found_in_ncbi = len(ncbi_id_to_ott_id)
num_found_in_synonyms = num_found_in_ncbi - num_found_in_taxonomy
debug("{} NCBI IDs found in {}".format(num_found_in_synonyms, synonyms_tsv))
old_ott_to_new = {}
forwards_tsv = os.path.join(ott_dir, 'forwards.tsv')
with codecs.open(forwards_tsv, 'rU', encoding='utf-8') as finp:
    for line in finp:
        if not line.strip():
            continue
        orig, replacement = [i.strip() for i in line.split('\t')]
        if orig == 'id':
            continue
        if orig in ott_id_seen:
            old_ott_to_new[orig] = replacement


gtdbid_to_ott_id = {}
ambig = set()
num_forwarded = 0
for ncbi_id, ottidset in ncbi_id_to_ott_id.items():
    gtdb_ids = ncbi_id_to_gtdbid_list[ncbi_id]
    num_matches = len(ottidset)
    if num_matches != 1:
        ltm = list(ottidset) if num_matches <= 5 else '[long list of IDs suppressed]'
        fmt = 'Dropping GTDB Ids {} ambiguously map via "NCBI:{}" to {} OTT IDs: {}'
        debug(fmt.format(gtdb_ids, ncbi_id, num_matches, ltm))
        for a in gtdb_ids:
            ambig.add(a)
    else:
        assert len(ottidset) == 1
        ott_id = list(ottidset)[0]
        if ott_id in old_ott_to_new:
            num_forwarded += 1
            ott_id = old_ott_to_new[ott_id]
        for gtdb_id in gtdb_ids:
            gtdbid_to_ott_id[gtdb_id] = ott_id
debug("{} OTT IDs had to be forwarded".format(num_forwarded))
debug("{} GTDB IDs mapped unambiguously to an OTT ID".format(len(gtdbid_to_ott_id)))

omitted = set()
for k, ncbi_id_list in gtdbid_to_ncbi_taxon_id.items():
    if k not in gtdbid_to_ott_id:
        if k not in ambig:
            omitted.add((k, ncbi_id_list))
m = "{} GTDB ids lost in mapping. {} due to ambiguity. {} for failing to find NCBI ID match in OTT. The latter are:\n{}"
x = '\n'.join(['{} -> "{}"'.format(i[0], i[1]) for i in omitted])
debug(m.format(len(ambig) + len(omitted), len(ambig), len(omitted), x))
out = sys.stdout
klist = list(gtdbid_to_ott_id)
klist.sort()

for k in klist:
    out.write('{}\t{}\n'.format(k, gtdbid_to_ott_id[k]))

