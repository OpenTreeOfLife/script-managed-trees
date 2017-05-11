# GTDB
This directory holds different version of trees created by
the Genome Tree Database effort by the 
http://ecogenomic.org/ project.

See https://github.com/Ecogenomics/GTDBNCBI

The trees are large trees of primarily bacterial taxa.
A mapping of GTDB IDs to NCBI taxon names is also provided.


## Usage
The top level script needs:
  1. the RefSeq number
  2. the path to an NCBI taxonomy in Open Tree Interim Taxonomy file format!
  3. the path to the OTT directory to use.
 
You also need to have the otcetera tools on your path for the last part of the
    pipeline.

Example:

    ./map-gtdb-to-ott.bash 78 /tmp/ncbi-20161109 /tmp/ott3.0draft6err-log-mapping-to-ncbi-id.txt

## Documentation of files
In a RefSeq# dir we'll have:

  1. `GTDB_RS#.tre` - input from GTDB newick with comment that has some documentation.
  2. `GTDB_RS#.txt` - input from GTDB mapping of labels to NCBI taxon names, note:
    * labels are not newick quoted in the tree, so have to convert _ to ' ' to
    match
    * NCBI taxon names with `=` have had that replaced with `/`
    * NCBI taxon names with `(` have been trimmed to remove that character
    (and preceding whitespace)
  3. `gtbd_id_to_ncbi_taxon_id.tsv` is an output that lists GTDB ID to NCBI
  taxon ID.
  4. `err-log-mapping-to-ncbi-id.txt` is the log file for the NCBI name ->
  taxon ID step
  5. `gtdb_id_to_ott_id.tsv` is an outpu that converts the mapping file
    to map to OTT IDs.
  6. `err-log-mapping-to-ott-id.txt` is the log file for the OTT mapping
    step
  7. `gtdb_id_to_ott_id_newick.tsv` is an output mapping that has the
  `_` to ` ` replacement of the GTDB labels.
  8. `mapped_gtdb_rs#.tre` is the output tree with "ott###" as tip labels 
  were the ### correspond to the OTT ID. Unmapped tips (and barren
  internals) will have been pruned.
  9. `err-log-pruning.txt` is the stderr log of that pruning operation.
  10. `pruning.json` is a JSON log of the tips pruned, the internal labels
    pruned are not useful in this case because the internal labels of the
    input are some support measure (some form or bootstrap percentage, I 
    think).
  11. `ncbi_about.json` is a copy of the `about.json` from the NCBI
  dir used.
  12. `ott_about.json` is a copy of the `about.json` from the OTT
  direcory used.



README.md
