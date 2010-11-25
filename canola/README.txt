agreement.py, stats*/, plan.fnlUsrAgrmnts, uids
Fleiss Multi-pi calculation of agreement on the basis of:
Artstein, Ron, and Massimo Poesio. "Inter-Coder Agreement for Computational Linguistics." Computational Linguistics 34, no. 4 (2008): 555-596. http://www.mitpressjournals.org/doi/abs/10.1162/coli.07-034-R2
$ ./agreement.py stats/ plan.canola UIDs
 stats*/: see below
 plan.fnlUsrAgrmnts: pageIDs to consider for agreement calculations
 uids: user IDs to consider

 out:
 # id: A_o A_o-weighted A_e A_e-weighted coef coef-weighted num(nodes) num(tokens)
 685: 0.811 0.572 0.010 0.015 0.809 0.566 84 677

 -id: pageID
 -A_o: observed agreement
 -A_e: expected agreement
 -coef: (A_o - A_e) / (1-A_e) - the actual multi-pi value
 -nodes: number of DOM nodes in the document
 -tokens: number of BTE-like tokens in the document
 -weighted: the respective calculations but weighted by the number of tokens

stats/, stats.20100908/ 
output of an app's merge run with -stats and plan.appErrsRmvd; for all
considered pageIDs there are two files:
pageID and pageID.stats
 - pageID: this is the HTML page after merging the different votes;
 -- the agreement on each tag is ( users-voted-for-the-tag / votes-on-the-tag )
    and is 'binned' in {0,10,20,...,100};
    the final tags look like krdwrd-tag-X-{0,10,20,...,100}
 - pageID.stats: the table with the individual users' votes on each tag

dumps_2nd/
JS-enabled re-dumps of pages for merging 
(during merge user submissions are compared to a 'master document' for
differences in text and structure. however, the user submissions' were done with
JS enabled (i.e. some might contain additional DOM nodes). therefore, the master
needs to be re-loaded with JS enabled.)

dumps_2nd.fl
pageIDs for files in dumps_2nd/

mkmerge.sh
produce merge*/ or stats*/ directories (cf. mkmerge.sh for more details)
$ mkdir /tmp/canola && ./mkmerge.sh plan.canola.appErrsRmvd 2>&1 | tee /tmp/canola/.log

plan.canola, merged.20100908.combined
THE pageIDs for the final corpus, and THE merged files
 - merged.20100908.combined: the .org files are the original output (similar
   to the files in the other merged.* dirs); to the actual files a pair of
   <html> tags was added:
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
[HERE the .org FILE]
</html>
"""

plan.appErrsRmvd, plan.mrgtieVotes, plan.mnlOvrwrt, plan.fnlUsrAgrmnts
intermediate pageIDs for producing the final corpus
 - plan.appErrsRmvd: only the IDs with technical hick-ups were removed, i.e.
   e.g. the app could not output a .png, or the content was partly https
 - plan.mrgtieVotes: pageIDs of pages where some nodes could not be assigned a 
   winner-takes-all final vote because of a tie (krdwrd-tag-mrgtie);
   these pages were processed with the app's '-finalmrg' option for the final
   corpus
 - plan.mnlOvrwrt: 3 pageIDs where the users' votes were /completely/ discarded
   for the final corpus and overwritten with a single submission

merged.20100908.plan.canola, merged.20100908.mrgtieVotes, merged.20100908.mnlOvrwrt
intermediate merges for producing the final corpus
 - merged.20100908.plan.canola: output of mkmerge.sh with plan.canola; with
 -- krdwrd-tag-mrgtie tags in case of a tie
 -- the merged pages for plan.mnlOvrwrt
 - merged.20100908.mrgtieVotes: output of mkmerge.sh with '-finalmrg'
   (cf. mkmerge.sh), and with plan.mrgtieVotes
 - merged.20100908.mnlOvrwrt: output of mkmerge.sh with plan.mnlOvrwrt and
   mkmerge.sh only considering one submission (cf.mkmerge.sh)
   
urls
mapping of pageIDs to original URLs
