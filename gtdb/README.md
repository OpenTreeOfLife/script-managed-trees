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

    ./map-gtdb-to-ott.bash 78 /tmp/ncbi-20161109 /tmp/ott3.0draft6