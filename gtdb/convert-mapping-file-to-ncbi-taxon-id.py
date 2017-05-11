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

num_mod_named = 0
ncbi_name_to_ncbi_tax_id_set = {}
def process_ncbi_name_id(name, ncbi_id):
    global num_mod_named
    if name in name_to_gtdbids:
        ncbi_name_to_ncbi_tax_id_set.setdefault(name, set()).add(ncbi_id)
    elif '=' in name:
        mod_name = name.replace('=', '/')
        if mod_name in name_to_gtdbids:
            debug('Found NCBI name by mimicking = to / replacement for {} to {}'.format(repr(name), repr(mod_name)))
            num_mod_named += 1
            ncbi_name_to_ncbi_tax_id_set.setdefault(mod_name, set()).add(ncbi_id)
    elif '(' in name:
        mod_name = name.split('(')[0].strip()
        if mod_name in name_to_gtdbids:
            debug('Found NCBI name by trimming ( or after  "{}"'.format(name))
            num_mod_named += 1
            ncbi_name_to_ncbi_tax_id_set.setdefault(mod_name, set()).add(ncbi_id)


taxonomy_tsv = os.path.join(ncbi_taxonomy_dir, 'taxonomy.tsv')
with codecs.open(taxonomy_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        process_ncbi_name_id(ls[2], ls[0])

num_found_in_taxonomy = len(ncbi_name_to_ncbi_tax_id_set)
debug("{} NCBI names found in {}".format(num_found_in_taxonomy, taxonomy_tsv))

synonyms_tsv = os.path.join(ncbi_taxonomy_dir, 'synonyms.tsv')
with codecs.open(synonyms_tsv, 'rU', encoding='utf-8') as ntinp:
    nti = iter(ntinp)
    nti.next()
    for line in nti:
        ls = line.split('\t|\t')
        process_ncbi_name_id(ls[1], ls[0])
num_found_in_ncbi = len(ncbi_name_to_ncbi_tax_id_set)
num_found_in_synonyms = num_found_in_ncbi - num_found_in_taxonomy
debug("{} NCBI names found in {}".format(num_found_in_synonyms, synonyms_tsv))
old_ncbi_to_new = {}
forwards_tsv = os.path.join(ncbi_taxonomy_dir, 'forwards.tsv')
with codecs.open(forwards_tsv, 'rU', encoding='utf-8') as finp:
    for line in finp:
        if not line.strip():
            continue
        orig, replacement = [i.strip() for i in line.split('\t')]
        if orig == 'id':
            continue
        old_ncbi_to_new[orig] = replacement


gtdbid_to_ncbi_taxon_id = {}
ambig = set()
num_forwarded = 0
for name, ntset in ncbi_name_to_ncbi_tax_id_set.items():
    gtdb_ids = name_to_gtdbids[name]
    num_matches = len(ntset)
    if num_matches != 1:
        ltm = list(ntset) if num_matches <= 5 else '[long list of IDs suppressed]'
        fmt = 'Dropping GTDB Ids {} ambiguously map via "{}" to {} NCBI IDs: {}'
        debug(fmt.format(gtdb_ids, name, num_matches, ltm))
        for a in gtdb_ids:
            ambig.add(a)
    else:
        assert len(ntset) == 1
        ntid = list(ntset)[0]
        if ntid in old_ncbi_to_new:
            num_forwarded += 1
            ntid = old_ncbi_to_new[ntid]
        for gtdb_id in gtdb_ids:
            gtdbid_to_ncbi_taxon_id[gtdb_id] = ntid
debug("{} NCBI taxon IDs had to be forwarded".format(num_forwarded))
debug("{} GTDB IDs mapped unambiguously to an NCBI taxon ID".format(len(gtdbid_to_ncbi_taxon_id)))

omitted = set()
for k, name in gtdbid_to_name.items():
    if k not in gtdbid_to_ncbi_taxon_id:
        if k not in ambig:
            omitted.add((k, name))
m = "{} GTDB ids lost in mapping. {} due to ambiguity. {} for failing to find a name match in NCBI. The latter are:\n{}"
x = '\n'.join(['{} -> "{}"'.format(i[0], i[1]) for i in omitted])
debug(m.format(len(ambig) + len(omitted), len(ambig), len(omitted), x))
out = sys.stdout
klist = list(gtdbid_to_ncbi_taxon_id)
klist.sort()

for k in klist:
    out.write('{}\t{}\n'.format(k, gtdbid_to_ncbi_taxon_id[k]))

