# Open Tree of Life script-managed trees
This directory is intended to hold large trees that are input to synthesis but are not
    in phylesystem because:
  1. Their large size makes manual curation in the curator app infeasible,
  2. Their large size makes storage in NexSON a poor choice,
  3. The entirely automated way of managing them calls requires no curation app.


# TODO
Lots todo..

  1. We probably want to create a phylesystem stub for each of these resources so that they:

     1. are more visible to users,
     2. can be ranked using the collections mechanism,
     3. can be indexed by OTI.
     4. can have their citations managed in a non ad hoc manner.

  2. We need to figure out where we will clone this repo on https://files.opentreeoflife.org
  3. Perhaps rethink this strategy of managing the files in a big git repo.
  4. External format: currently newick with tip labels all like ott<num>.

     * We need node labels for running conflict, in addition to other reasons.
     * We _could_ make the conflict service add these labels where they are missing.  Maybe with a flag like "generate_node_names": true
     * However, if these node labels are not persistent that could be a problem.
     * Lets use the mrcaottXottY format to add node labels that would persist better.

  5. So: extend nexson format
    * Remove: otusByID.
    * Keep: treesById
      * Remove treesById[groupname]["@otus"],
      * Remove treesById[groupname]["^otTreeElementOrder"],
      * Keep   treesById[groupname]["treeByID"][treename]     
      * Add    treesById[groupname]["treeByID"][treename]["external-data"] = {"url":url, "format":format}
      * Remove treesById[groupname]["treeByID"][treename]["edgeBySourceId"]
      * Remove treesById[groupname]["treeByID"][treename]["nodeById"]

  6. Modifying downstream consumers:
    1. propinquity
       * We might need a SHA for the downloaded file.  We could replace the format SHA with the formath SHA_SHA_DATE, but just for external trees.
    2. ws_wrapper: currently uses PhyloSchema( ) to get newick from nexson
       * Maybe add a more general function to get a tree from a nexson?
    3. curator:
       * Can we edit extended files to e.g. add DOI, citation?
         * Depends if the curator preserves fields that it does not understand.
         * We could make it understand the "^ot:external_tree" field.
       * Disable functionality: mapping, viewing (?)
       * Enable  functionality: 
    4. peyotl:
       * What functions to modify in peyotl?
       * Can we get some of the functionality transparently by making peyotl functions handle external trees?

