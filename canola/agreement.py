#!/usr/bin/env python

import os
import sys
import numpy as np

arg_statsdir=1 # output of krdwrd app's -merge
arg_plan=2 # file with page ids to consider
arg_uids=3 # file with user ids to consider
# Usage: $0 stats/ plan.canola uids

def main():
    name_statsdir = sys.argv[arg_statsdir]
    name_plan = sys.argv[arg_plan]
    name_uids = sys.argv[arg_uids]

    plan = [ln.strip() for ln in file(name_plan).readlines()]
    uids = [ln.strip() for ln in file(name_uids).readlines()]
    list_array_stats = read_stats(plan,name_statsdir)
    list_array_stats = check_stats_uids(uids,list_array_stats)

    # per list entry:
    #  sts: submitters, tks: tokens, wts: winning tags, sss: submissions
    # list_dict_array_stats 
    lda_stats = mk_list_dict_array_stats(list_array_stats)

    # sum of tokens and nodes in all stats
    sum_tokens, sum_nodes = mk_sum_toknnodes(lda_stats)

    print "#",len(plan),"files,",len(uids),"users" 
    print "#",sum_nodes,"nodes,",sum_tokens,"tokens"

    # over-all agreement - with and without weight
    sum_Ao = sum_Aow = sum_Ae = sum_Aew = sum_coef = sum_coefw = 0
    print "#","id:","A_o","A_o-weighted","A_e","A_e-weighted","coef","coef-weighted","num(nodes)","num(tokens)"
    for idx in range(len(lda_stats)):
        Ao = A_o(lda_stats[idx]['sss'])
        Aow = A_o(lda_stats[idx]['sss'], lda_stats[idx]['tks'])
        sum_Ao = sum_Ao + Ao * len(lda_stats[idx]['wts'])
        sum_Aow = sum_Aow + Aow * sum(lda_stats[idx]['tks'])
        
        Ae = A_e(lda_stats[idx]['sss'])
        Aew = A_e(lda_stats[idx]['sss'], lda_stats[idx]['tks'])
        sum_Ae = sum_Ae + Ae * len(lda_stats[idx]['wts'])
        sum_Aew = sum_Aew + Aew * sum(lda_stats[idx]['tks'])

        coef = Coef(Ao,Ae)
        coefw = Coef(Aow,Aew)
        sum_coef = sum_coef + coef * len(lda_stats[idx]['wts'])
        sum_coefw = sum_coefw + coefw * sum(lda_stats[idx]['tks'])

        print plan[idx]+':',
        print "%0.3f" % (Ao),
        print "%0.3f" % (Aow),
        print "%0.3f" % (Ae),
        print "%0.3f" % (Aew),
        print "%0.3f" % (coef),
        print "%0.3f" % (coefw),
        print len(lda_stats[idx]['wts']), sum(lda_stats[idx]['tks'])

    print "#","all:",
    print "%0.3f" % (float(sum_Ao) / sum_nodes),
    print "%0.3f" % (float(sum_Aow) / sum_tokens),
    print "%0.3f" % (float(sum_Ae) / sum_nodes),
    print "%0.3f" % (float(sum_Aew) / sum_tokens),
    print "%0.3f" % (float(sum_coef) / sum_nodes),
    print "%0.3f" % (float(sum_coefw) / sum_tokens)

def Coef(Ao,Ae):
    return (Ao - Ae) / (1-Ae)

def A_e(submissions, weights = []):
    """
    Expected Agreement for all user submissions of one page
    """
    num_nodes = len(submissions) + sum(weights)    # number of items/nodes
    num_coders = len(submissions[0])

    categories = set()
    for subs in submissions:
        categories = categories.union(set(subs))

    sum_keK = 0
    for idx in range(len(submissions)):
        try: weight = weights[idx]
        except IndexError: weight = 1
        for k in categories:
            n = (np.array(submissions[idx])==k).sum()
            sum_keK = sum_keK + (n * weight) **2
    return ( 1.0 / ( num_nodes * num_coders )**2 ) * sum_keK

def A_o(submissions, weights = []):
    """
    Overall observed Agreement for all user submissions of one page

    submissions: 'the set of Items' - in our case the individual users' votes on 
     each item
    """
    num_nodes = len(submissions) + sum(weights)    # number of items/nodes
    
    sum_agr_i = 0
    for idx in range(len(submissions)):
        try: weight = weights[idx]
        except IndexError: weight = 1
        # print submissions[idx], weight
        sum_agr_i = sum_agr_i + agr_i(submissions[idx]) * weight
    return ( 1.0 / num_nodes ) * sum_agr_i

def agr_i(n_ss):
    """
    Amount of Agreement on a particular item/node
    """
    c = len(n_ss)   # number of coders
    # print c,"coders,",
    
    sum_keK = 0
    for k in set(n_ss): # yields the set of Categories
        # number of times item i is classified as category k
        n_ik = (np.array(n_ss)==k).sum()
        # print k,":",n_ik,', ',
        sum_keK = sum_keK + (n_ik * (n_ik-1))
    return ( ( 1.0 / ( c * (c-1) ) ) * sum_keK )

def mk_sum_toknnodes(stats):
    sum_nodes = sum_tokens = 0
    for stat in stats:
        sum_tokens = sum_tokens + sum(stat['tks'])
        sum_nodes = sum_nodes + len(stat['wts'])
    return sum_tokens, sum_nodes

def mk_list_dict_array_stats(stats):
    for idx in range(len(stats)):
        stat = stats[idx]
        sstat = dict() 
        sstat['sts'] = [int(x) for x in stat[0,2:]] # submitters
        sstat['tks'] = [int(x) for x in stat[1:,0]] # tokens
        sstat['wts'] = stat[1:,1]                   # winning tags
        sstat['sss'] = np.array(stat[1:,2:])        # submissions
        
        stats[idx] = sstat
    return stats

def check_stats_uids(uids, stats):
    for stat in stats:
        for uid in stat[0][2:]:
            if (uid not in uids): raise Exception, """Found unknown submitter uid:"""+uid+""" in submissions.""" 
    return stats

def clean_stat(stat):
    # first row is comment
    stat = stat[1:]
    # get rid of '\n' at the end of line 
    stat = [ln.strip() for ln in stat]
    # now, first (former second) row has colnames (# col1\tcol2\tcol3...)
    stat[0] = [ln.strip('# ') for ln in stat[0].split('\t')]
    # s/krdwrd-tag-*/\1/
    for ln in range(1,len(stat)):
        stat[ln] = [elem.replace("krdwrd-tag-","") for elem in stat[ln].split()]
        # stat[ln] = [elem.replace("krdwrd-tag-2","krdwrd-tag-1").replace("krdwrd-tag-","") for elem in stat[ln].split()]

    # cut off end-of stat failed-merge info
    st = list()
    for s in range(len(stat)):
        if (stat[s][1] != "undefined"): st.append(stat[s])
        else: 
            for chck in stat[s:]:
                if (chck[1] != "undefined"):
                    # this should not happen: 'undefined' in [1] means
                    # that some submits have additional nodes, i.e.
                    # continuous list only at the end of [1]
                    raise Exception, """Found "undefined" in merge column."""
            break

    return st

def read_stats(plan,dir):
    stats = list()
    for p in plan:
        cstat = clean_stat(file(dir+os.path.sep+p+".stats").readlines())
        stats.append(np.array(cstat))

    return stats

if __name__ == "__main__": main()
