#!/usr/bin/env bash

BASE="https://krdwrd.org/pages"
APP=${HOME}/krdwrd/trunk/src/app/krdwrd

PAGEID=$1
declare -a SUBMS
declare ind=0

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
${APP} -merge ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html ${SUBMS[@]} -out /tmp/canola/${PAGEID} -sloppy -stats 2>/dev/null 
#xulrunner application.ini -merge ${BASE}/dat/canola/dumps_2nd/${PAGEID}.html ${SUBMS[@]} -out /tmp/canola/${PAGEID} -sloppy -victor
