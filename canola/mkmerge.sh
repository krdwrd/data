#!/usr/bin/env bash

# Xvfb :77 -screen 0 1024x768x24 >/dev/null 2>&1 &
# export DISPLAY=0:77

BASE="https://krdwrd.org/pages"

PLAN=$1
OUT=$2
krdwrd=${HOME}/krdwrd/trunk/src/app/krdwrd

# discard submissions from these userIDs
BADUIDS=(14 31 34 73 74)
#BADUIDS=()


function elem {
    MYELEM=$1
    shift
    for i in "$@"; do 
        if [[ $i == ${MYELEM} ]] ; then 
            return 0 
        fi 
    done
    return 1  
}

for PAGEID in $(cat $PLAN)
do
    unset SUBMS
    declare -a SUBMS
    declare ind=0
    for userid in $(wget http://krdwrd.org/db/submuids/${PAGEID} --quiet -O -); do
        if !( elem ${userid} "${BADUIDS[@]}" ); then
            SUBMS[${ind}]=${BASE}/bin/subm/${PAGEID}/${userid}
        else
            echo "# discarding banned user ${userid}."
        fi
        let ind+=1
    done

    echo ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html
    echo ${SUBMS[@]}
    ## use PAGEIDs from PLAN to merge user submissions for these pages
    ## add "-stats" 
    ##  for krdwrd-tag-x-BINs and .stats-files
    ${krdwrd} -merge ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html ${SUBMS[@]} -out ${OUT}/${PAGEID} -sloppy -proxy "http://proxy.krdwrd.org:8080"
    #
    ## use document from VOTEID as additional vote - in case of another mrgtie let
    ## VOTEID give the decisive answer  
    #VOTEID=2
    #${krdwrd} -merge ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html ${SUBMS[@]} ${BASE}/bin/subm/${PAGEID}/${VOTEID} -out ${OUT}/${PAGEID} -sloppy -proxy "http://proxy.krdwrd.org:8080" -finalmrg
    #
    ## use PAGEIDs from PLAN as single votes - this overwrites users' votes with a
    ## single one
    #${krdwrd} -merge ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html ${BASE}/bin/subm/${PAGEID}/2 -out ${OUT}/${PAGEID} -sloppy -proxy "http://proxy.krdwrd.org:8080"
done
