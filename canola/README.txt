agreement/
Fleiss Multi-pi calculation of agreement on the basis of:
Artstein, Ron, and Massimo Poesio. "Inter-Coder Agreement for Computational Linguistics." Computational Linguistics 34, no. 4 (2008): 555-596. http://www.mitpressjournals.org/doi/abs/10.1162/coli.07-034-R2


pagedata.py, analyse_pagedata.r, and stats*/
./pagedata.py stats page.csv user.csv userpage.csv pagenodeusertags.csv
 IN stats/: stats directory from an app's -merge -stats run
 OUT page.csv user.csv userpage.csv pagenodeusertags.csv:
    cf. page.csv.txt, user.csv.txt, userpage.csv.txt
    pagenodeusertags.csv: needed for agreement
 
 all sorts of measures of the quality/difficulty/etc. of submissions/pages


timings/
take deltas between submissions and calculate durations users saw pages


dumps_2nd/
JS-enabled re-dumps of pages for merging 
(during merge user submissions are compared to a 'master document' for
differences in text and structure. however, the user submissions' were done with
JS enabled (i.e. some might contain additional DOM nodes). therefore, the master
needs to be re-loaded with JS enabled.)

dumps_2nd.fl
pageids


mkstats.sh
 for pageid in (cat dumps_2nd.fl); do ./mkstats.sh $pageid; done
    merge user submissions (from dumps_2ns) and produce stats/


submissions.tar.bz2
DB dumps of user submissions
