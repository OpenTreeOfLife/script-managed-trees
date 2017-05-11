#!/usr/bin/env python
import codecs
import sys
import os

script_name = os.path.split(sys.argv[0])[-1]


def debug(m):
    sys.stderr.write("{}: {}\n".format(script_name, m))

try:
    to_ott_id_file = sys.argv[1]
    assert os.path.isfile(to_ott_id_file)
except:
    sys.exit("Expecting 1 arguments: the mapping file from GTDB ID to OTT ID")
out = sys.stdout
with codecs.open(to_ott_id_file, 'rU', encoding='utf-8') as minp:
    for line in minp:
        ls = line.strip()
        if not ls:
            continue
        try:
            gtdb_id, ncbi_taxon_id = [i.strip() for i in ls.split('\t')]
            if "'" in gtdb_id:
                out.write(line)
            else:
                gtdb_id = gtdb_id.replace('_', ' ')
                out.write('{}\t{}\n'.format(gtdb_id, ncbi_taxon_id))
        except:
            sys.exit("Expecting 1 tab in a  non-empty line. Found:\n{}".format(line))
