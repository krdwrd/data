#! /usr/bin/env python2.5 

__author__= "martisch@uos.de"
__date__  = "$Feb 21, 2009 18:14:02 PM$"

import os
import shutil
from time import strptime, strftime
from collections import defaultdict
from scipy import stats


submissions_filename = 'submissions.txt'
pages_filename = 'pages.txt'

durationdata_filename = 'duration.data'
statistics_filename = 'statistics.csv'
userhistory_filename = '_userstats.data'
statdir = 'stats'

timeframe_threshold = 3600 # =< in seconds
#timeframe_threshold = 500000 # =< in seconds
highest_training_pageid = 500

def main():
    users_dict = read_submissions(submissions_filename)
    pages_dict = read_pages(pages_filename)
    stats_dict = init_statsdict(users_dict)
    make_statdir()
    compute_timeframes(users_dict)
    filter_training(users_dict)
    merge_continioussubmissions(users_dict,stats_dict)
    filter_threshold(users_dict,stats_dict)
    dump_userstats(users_dict)
    dump_durationdata(users_dict)
    #detect_duplicates(users_dict)
    compute_gradient(users_dict,stats_dict)
    pagetime_dict = merge_multisubmissions(users_dict,stats_dict)
    compute_userstats(pagetime_dict,stats_dict)
    dump_stats(stats_dict)

def make_statdir():
    if os.path.isdir(statdir): 
        shutil.rmtree(statdir)
    os.mkdir(statdir)
    
def dump_userstats(users_dict):
    for userid in users_dict.keys():
        file = open(statdir+'/'+str(userid)+userhistory_filename,'w')
        file.write('\n'.join([str(elem[2]) for elem in users_dict[userid]])+'\n')
        file.close()
    
def dump_durationdata(users_dict):
    file = open(statdir+'/'+durationdata_filename,'w')
    for data in users_dict.values():
        file.write('\n'.join([str(elem[2]) for elem in data])+'\n')
    file.close()

def dump_stats(stats_dict):
    rownames = set()
    for data in stats_dict.values():
        rownames.update(data.keys())
    rownames = sorted(list(rownames))
    file = open(statdir+'/'+statistics_filename,'w')
    file.write(','.join(['userid']+rownames)+"\n")
    for userid in sorted(stats_dict.keys()):
        data = stats_dict[userid]
        file.write(','.join([str(userid)]+[str(data[key]) for key in rownames])+'\n')
    file.close()

def init_statsdict(users_dict):
    return dict([(userid,defaultdict(int)) for userid in users_dict.keys()])

def compute_gradient(users_dict,stats_dict):
    for userid in users_dict.keys():
        durations = [elem[2] for elem in users_dict[userid]]
        gradient, intercept, r_value, p_value, std_err = stats.linregress(xrange(len(durations)),durations)    
        stats_dict[userid]['gradient_pagetime']=gradient

def compute_userstats(pagetime_dict,stats_dict):
    for userid in pagetime_dict.keys():
        durations = pagetime_dict[userid].values()
        stats_dict[userid]['max_pagetime']=max(durations)
        stats_dict[userid]['min_pagetime']=min(durations)
        stats_dict[userid]['mean_pagetime']=stats.mean(durations)
        stats_dict[userid]['variance_pagetime']=stats.var(durations)
        stats_dict[userid]['total_pagetime']=sum(durations)
        stats_dict[userid]['numdata_pagetime']=len(durations)

def detect_duplicates(users_dict):
    for userid in users_dict.keys():
        pages = [elem[1] for elem in users_dict[userid]]
        if len(pages)!=len(set(pages)):
            print "WARNING: duplicate submits for userid: ", userid ," ... deleting data."

def merge_continioussubmissions(users_dict,stats_dict):
    for userid in users_dict.keys():
        data = users_dict[userid]
        stats_dict[userid]['num_submisson']=len(data)
        i = 1
        while i < len(data):
            if data[i][1]==data[i-1][1]:
                data[i-1][2] += data[i][2]
                del data[i]
                stats_dict[userid]['cont_submisson']+=1
            else:
                i+=1

def merge_multisubmissions(users_dict,stats_dict):
    pagetime_dict = dict()
    for userid in users_dict.keys():
        data = users_dict[userid]
        userpagetime_dict = defaultdict(int)
        for (time,pageid,duration) in data:
            if userpagetime_dict.has_key(pageid):
                stats_dict[userid]['multi_submisson']+=1
            userpagetime_dict[pageid]+=duration
        pagetime_dict[userid] = userpagetime_dict
    return pagetime_dict
    
def filter_training(users_dict):
    for userid in users_dict.keys():
        users_dict[userid] = [elem for elem in users_dict[userid] if elem[1] > highest_training_pageid]

def filter_threshold(users_dict,stats_dict):
    for userid in users_dict.keys():
        data = users_dict[userid]
        temp = len(users_dict[userid])
        data = [elem for elem in data if elem[2] <= timeframe_threshold]
        stats_dict[userid]['tolong_submisson']= (temp - len(data))
        if len(data)==0:
            del users_dict[userid]
        else:
            users_dict[userid] = data
        
        
def compute_timeframes(users_dict):
    for userid in users_dict.keys():
        data = users_dict[userid]
        data.sort()
        for i in xrange(1,len(data)):
            data[i].append(data[i][0] - data[i - 1][0])
        del data[0] #cant compute time for first one
        
def read_submissions(filename):
    user_dict = defaultdict(list)
    lines = open(filename,'r').readlines()
    for line in lines:
        data = line.strip().split('|')
        user_id , page_id = [int(string) for string in data[:-1]]
        unixtime = int(strftime('%s',strptime(data[-1], '%Y-%m-%d %H:%M:%S')))
        user_dict[user_id].append([unixtime, page_id])
    return user_dict


def read_pages(filename):
    pages_dict = dict()
    lines = open(filename,'r').readlines()
    for line in lines:
        corpus_id , page_id = [int(string) for string in line.strip().split('|')]
        pages_dict[page_id] = corpus_id
    return pages_dict

if __name__ == "__main__":
    main()
