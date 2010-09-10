#!/usr/bin/env python

import os
import sys
from math import log
from collections import defaultdict
from itertools import izip,count

novaluestr = 'none'
endl = '\n'
delimiter = ','
in_arg = 1
out_arg_pagestats = 2
out_arg_userstats = 3
out_arg_userpagestats = 4
out_arg_pagenoderusertags = 5

# differ rating , differ tag per document / user


def main():
    in_foldername = sys.argv[in_arg]
    out_filename_pagestats = sys.argv[out_arg_pagestats]
    out_filename_userstats = sys.argv[out_arg_userstats]
    out_filename_userpagestats = sys.argv[out_arg_userpagestats]
    out_filename_pagenoderusertags = sys.argv[out_arg_pagenoderusertags]
    stats_dict = dict()
    data,metadata = collect_chunks(in_foldername)
    statsadd(stats_dict,tagstats(data,'raw'))
    statsadd(stats_dict,pagestats(data,'raw'))
    statsadd(stats_dict,userstats(metadata,'raw'))
    aligndomtree(data,metadata)
    statsadd(stats_dict,tagstats(data,'withmerge'))
    statsadd(stats_dict,pagestats(data,'withmerge'))
    statsadd(stats_dict,userstats(metadata,'withmerge'))
    #print_stats(stats_dict)
    statsadd(stats_dict,page_rating(data,metadata))
    userdata,userpagedata = user_rating(data,metadata)
    userdata_output(userdata,out_filename_userstats)
    pagedata_output(stats_dict,out_filename_pagestats)
    pagenoderusertags_output(data,metadata,out_filename_pagenoderusertags)
    userpagedata_output(userpagedata,out_filename_userpagestats)

def pagenoderusertags_output(data,metadata,filename):
    file = open(filename,'w')
    file.write(delimiter.join(['pageid','nodeid','userid','tag'])+endl)
    for pageid,pagedata in data.items():
        userids = metadata[pageid]['userids']
        for nodeid,nodedata in pagedata.items():
            for userid,tag in zip(userids,nodedata):
                file.write(delimiter.join([str(pageid),str(nodeid+1),str(userid),str(tag)])+'\n')
    file.close()
                
                
def user_rating(data,metadata):
    userdata = dict()
    userpagedata = dict()
    for userid in set(sum([pagemetadata['userids'] for pagemetadata in metadata.values()],[])):
        userdata[userid] = defaultdict(int)
        userpagedata[userid] = dict()
    for pageid,pagedata in data.items():
        userids = metadata[pageid]['userids']
        for userid in userids:
            userpagedata[userid][pageid] = defaultdict(int)
        for nodeid,nodedata in pagedata.items():
            nodetag    = metadata[pageid]['tag'][nodeid]
            noderating = metadata[pageid]['rating'][nodeid]
            chars      = metadata[pageid]['chars'][nodeid]
            for userid,tag in zip(userids,nodedata):
                userpagedata_userid_pageid = userpagedata[userid][pageid]
                userdata[userid][str(tag)] += 1
                if tag!='none':
                    bias_tag = tag-nodetag
                    bias_rating = tag-noderating
                    userdata[userid]['difficulty_rating']                += abs(nodetag-noderating)
                    userdata[userid]['weighted_difficulty_rating']       += chars*userdata[userid]['difficulty_rating']
                    userpagedata_userid_pageid['count_tag']              += 1
                    userpagedata_userid_pageid['sum_chars']              += chars
                    userpagedata_userid_pageid['bias_tag']               += bias_tag
                    userpagedata_userid_pageid['weighted_bias_tag']      += chars*bias_tag
                    userpagedata_userid_pageid['bias_rating']            += bias_rating
                    userpagedata_userid_pageid['weighted_bias_rating']   += chars*bias_rating
                    userpagedata_userid_pageid['differ_tag']             += abs(bias_tag)
                    userpagedata_userid_pageid['weighted_differ_tag']    += chars*abs(bias_tag)
                    userpagedata_userid_pageid['differ_rating']          += abs(bias_rating)
                    userpagedata_userid_pageid['weighted_differ_rating'] += chars*abs(bias_rating)
                    if bias_tag > 0:
                        userpagedata_userid_pageid['sum_chars_pos_bias_tag'] += chars
                        userpagedata_userid_pageid['sum_weighted_pos_bias_tag'] += chars*bias_tag
                        userpagedata_userid_pageid['sum_pos_bias_tag'] += bias_tag
                        userpagedata_userid_pageid['num_pos_bias_tag'] += 1
                    elif bias_tag < 0:
                        userpagedata_userid_pageid['sum_chars_neg_bias_tag'] += chars
                        userpagedata_userid_pageid['sum_weighted_neg_bias_tag'] += chars*bias_tag
                        userpagedata_userid_pageid['sum_neg_bias_tag'] += bias_tag
                        userpagedata_userid_pageid['num_neg_bias_tag'] += 1
                    if bias_rating > 0:
                        userpagedata_userid_pageid['sum_chars_pos_bias_rating'] += chars
                        userpagedata_userid_pageid['sum_weighted_pos_bias_rating'] += chars*bias_rating
                        userpagedata_userid_pageid['sum_pos_bias_rating'] += bias_rating
                        userpagedata_userid_pageid['num_pos_bias_rating'] += 1
                    elif bias_rating < 0:
                        userpagedata_userid_pageid['sum_chars_neg_bias_rating'] += chars
                        userpagedata_userid_pageid['sum_weighted_neg_bias_rating'] += chars*bias_rating
                        userpagedata_userid_pageid['sum_neg_bias_rating'] += bias_rating
                        userpagedata_userid_pageid['num_neg_bias_rating'] += 1    
        for userid in userids:
            userdata_userid = userdata[userid]
            userpagedata_userid_pageid = userpagedata[userid][pageid]
            userdata_userid['count_tag']              += userpagedata_userid_pageid['count_tag']
            userdata_userid['sum_chars']              += userpagedata_userid_pageid['sum_chars']
            userdata_userid['bias_tag']               += userpagedata_userid_pageid['bias_tag']
            userdata_userid['weighted_bias_tag']      += userpagedata_userid_pageid['weighted_bias_tag']
            userdata_userid['bias_rating']            += userpagedata_userid_pageid['bias_rating']
            userdata_userid['weighted_bias_rating']   += userpagedata_userid_pageid['weighted_bias_rating']
            userdata_userid['differ_tag']             += userpagedata_userid_pageid['differ_tag']
            userdata_userid['weighted_differ_tag']    += userpagedata_userid_pageid['weighted_differ_tag']
            userdata_userid['differ_rating']          += userpagedata_userid_pageid['differ_rating']            
            userdata_userid['weighted_differ_rating'] += userpagedata_userid_pageid['weighted_differ_rating']            
    return (userdata,userpagedata)

def userpagedata_output(userpagedata,filename):
    file = open(filename,'w')
    keys = sorted(userpagedata.values()[0].values()[0].keys())
    file.write(delimiter.join(['userid','pageid']+keys)+endl)
    for userid,userdata in userpagedata.items():
        file.writelines([delimiter.join(map(str,[userid,pageid]+[data[key] for key in keys]))+endl for pageid,data in sorted(userdata.items())])
    file.close()

def pagedata_output(pagedata,filename):
    file = open(filename,'w')
    keys = sorted(list(set(sum([page.keys() for pageid,page in pagedata.items() if pageid!='overall'],[]))))
    file.write(delimiter.join(['pageid']+keys)+endl)
    file.writelines([delimiter.join(map(str,[pageid]+[data.get(key,novaluestr) for key in keys]))+endl for pageid,data in sorted(pagedata.items()) if pageid!='overall'])
    file.close()


def userdata_output(userdata,filename):
    file = open(filename,'w')
    keys = sorted(list(set(sum([user.keys() for user in userdata.values()],[]))))
    file.write(delimiter.join(['userid']+keys)+endl)
    file.writelines([delimiter.join(map(str,[userid]+[data[key] for key in keys]))+endl for userid,data in sorted(userdata.items())])
    file.close()

def page_rating(data,metadata):
    value_dict = dict()
    for pageid,pagedata in data.items():
        metadata[pageid]['rating'] = dict()
        metadata[pageid]['weighted_rating'] = dict()
        metadata[pageid]['tag'] = dict()
        metadata[pageid]['weighted_tag'] = dict()
        metadata[pageid]['difficulty'] = dict()
        metadata[pageid]['weighted_difficulty'] = dict()
        metadata[pageid]['bias'] = dict()
        metadata[pageid]['weighted_bias'] = dict()
        metadata[pageid]['sum_chars_pos_bias'] = 0
        metadata[pageid]['sum_weighted_pos_bias'] = 0
        metadata[pageid]['sum_pos_bias'] = 0
        metadata[pageid]['num_pos_bias'] = 0
        metadata[pageid]['sum_chars_neg_bias'] = 0
        metadata[pageid]['sum_weighted_neg_bias'] = 0
        metadata[pageid]['sum_neg_bias'] = 0
        metadata[pageid]['num_neg_bias'] = 0
        for nodeid,nodedata in sorted(pagedata.items()):
            cleannodedata = [value for value in nodedata if value!='none']
            metadata[pageid]['chars'][nodeid] = int(metadata[pageid]['chars'][nodeid])
            metadata[pageid]['rating'][nodeid] = sum(cleannodedata)/float(len(cleannodedata))
            metadata[pageid]['weighted_rating'][nodeid] = metadata[pageid]['rating'][nodeid]*metadata[pageid]['chars'][nodeid]
            metadata[pageid]['tag'][nodeid] = round(metadata[pageid]['rating'][nodeid])
            metadata[pageid]['weighted_tag'][nodeid] = metadata[pageid]['tag'][nodeid]*metadata[pageid]['chars'][nodeid] 
            metadata[pageid]['difficulty'][nodeid] = abs(metadata[pageid]['tag'][nodeid]-metadata[pageid]['rating'][nodeid])
            metadata[pageid]['weighted_difficulty'][nodeid] = metadata[pageid]['difficulty'][nodeid]*metadata[pageid]['chars'][nodeid]
            metadata[pageid]['bias'][nodeid] = metadata[pageid]['tag'][nodeid]-metadata[pageid]['rating'][nodeid]
            metadata[pageid]['weighted_bias'][nodeid] = metadata[pageid]['bias'][nodeid]*metadata[pageid]['chars'][nodeid]
            if metadata[pageid]['bias'][nodeid] > 0:
                metadata[pageid]['sum_chars_pos_bias'] += metadata[pageid]['chars'][nodeid]
                metadata[pageid]['sum_weighted_pos_bias'] += metadata[pageid]['bias'][nodeid]*metadata[pageid]['chars'][nodeid]
                metadata[pageid]['sum_pos_bias'] += metadata[pageid]['bias'][nodeid]
                metadata[pageid]['num_pos_bias'] += 1
            elif metadata[pageid]['bias'][nodeid] < 0:
                metadata[pageid]['sum_chars_neg_bias'] += metadata[pageid]['chars'][nodeid]
                metadata[pageid]['sum_weighted_neg_bias'] += metadata[pageid]['bias'][nodeid]*metadata[pageid]['chars'][nodeid]
                metadata[pageid]['sum_neg_bias'] += metadata[pageid]['bias'][nodeid]
                metadata[pageid]['num_neg_bias'] += 1
        metadata[pageid]['sum_chars'] = sum([number for number in metadata[pageid]['chars'] if number!='undefined'])
        metadata[pageid]['sum_bias'] = sum(metadata[pageid]['bias'].values())
        metadata[pageid]['sum_weighted_bias'] = sum(metadata[pageid]['weighted_bias'].values())
        metadata[pageid]['diversity_rating'] = sum([abs(before[1]-after[1]) for before,after in zip(sorted(metadata[pageid]['rating'].items())[1:],sorted(metadata[pageid]['rating'].items())[:-1])])
        metadata[pageid]['diversity_tag'] = sum([abs(before[1]-after[1]) for before,after in zip(sorted(metadata[pageid]['tag'].items())[1:],sorted(metadata[pageid]['tag'].items())[:-1])])
        metadata[pageid]['sum_difficulty'] = sum(metadata[pageid]['difficulty'].values())
        metadata[pageid]['sum_weighted_difficulty'] = sum(metadata[pageid]['weighted_difficulty'].values())
        metadata[pageid]['average_rating'] = sum(metadata[pageid]['rating'].values())/len(pagedata)
        metadata[pageid]['average_weighted_rating'] = sum(metadata[pageid]['weighted_rating'].values())/metadata[pageid]['sum_chars']
        metadata[pageid]['average_tag'] = sum(metadata[pageid]['tag'].values())/len(pagedata)
        metadata[pageid]['average_weighted_tag'] = sum(metadata[pageid]['weighted_tag'].values())/metadata[pageid]['sum_chars']
        metadata[pageid]['tag_by_average_rating'] = round(metadata[pageid]['average_rating'])
        metadata[pageid]['tag_by_weighthed_average_rating'] = round(metadata[pageid]['average_weighted_rating'])
        metadata[pageid]['tag_by_average_tag'] = round(metadata[pageid]['average_tag'])
        metadata[pageid]['tag_by_weighthed_average_tag'] = round(metadata[pageid]['average_weighted_tag'])
        #print pageid,metadata[pageid]['averagetag'],metadata[pageid]['averagerating'],metadata[pageid]['tag_by_averagetag'],metadata[pageid]['tag_by_averagerating']
        value_dict[pageid] = dict()
        for key,data in metadata[pageid].items():
            if not type(data)==dict and not type(data)==list:
                value_dict[pageid][key] = data
    return value_dict
        
def statsadd(stats_dict,new_dict):
    for id,data in new_dict.items():
        if not stats_dict.has_key(id):
            stats_dict[id] = dict()    
        stats_dict[id].update(data)

def print_stats(stats_dict):
    for stat, value in sorted(stats_dict['overall'].items()):
        print stat, value
    
def aligndomtree(data,metadata):
    for pageid,pagedata in data.items():
        domnodes_length = len([True for tag in metadata[pageid]['mergetags'] if tag != 'undefined'])
        if not domnodes_length:
            print 'document ' + pageid + ' has no valid alignments with user submissions'
            del data[pageid]
            del metadata[pageid]
        else:
            for index,id in reversed(list(enumerate(metadata[pageid]['userids']))):
                domnodes_count = len([True for tags in pagedata.values() if tags[index] != 'undefined']) 
                if domnodes_count != domnodes_length:
                    print 'deleting user ' + str(id) + ' from document ' + pageid + ' due to misalignment'
                    userids = metadata[pageid]['userids']
                    metadata[pageid]['userids'] = userids[:index]+userids[index+1:] 
                    for nodeid,tags in pagedata.items():
                        pagedata[nodeid] = tags[:index]+tags[index+1:]
            assert(len(pagedata) >= domnodes_length)
            assert(len(metadata[pageid]['userids']) > 0)
            for index in xrange(domnodes_length,len(pagedata)):
                del pagedata[index]
            assert(len(pagedata) > 0)

def userstats(metadata,prefix):
    value_dict = dict({'overall':defaultdict(int)})
    value_dict['overall'][prefix + '_unique_userids'] = len(set(sum([pagemetadata['userids'] for pagemetadata in metadata.values()],[])))
    return value_dict

def pagestats(data,prefix):
    value_dict = dict({'overall':defaultdict(int)})
    for pageid,pagedata in data.items():
        value_dict[pageid] = defaultdict(int)
        value_dict[pageid][prefix + '_page_userids'] = len(pagedata.values()[0])
        value_dict[pageid][prefix + '_page_domnodes'] = len(pagedata.keys())
        value_dict['overall'][prefix + '_page_userids'] += value_dict[pageid][prefix + '_page_userids']
        value_dict['overall'][prefix + '_page_domnodes'] += value_dict[pageid][prefix + '_page_domnodes']      
    return value_dict

def tagstats(data,prefix):    
    value_dict = dict({'overall':defaultdict(int)})
    for pageid, pagedata in data.items():
        value_dict[pageid] = defaultdict(int)
        for value in sum(pagedata.values(),[]):
            value_dict[pageid][prefix + '_tag_' + str(value)] += 1
            value_dict['overall'][prefix + '_tag_' + str(value)] += 1
    return value_dict
    
def collect_chunks(folder):
    data = dict()
    metadata = dict()
    for filename in os.listdir(folder):
        file = open(folder+os.path.sep+filename,'r')
        pageid = filename.split('.')[0]
        data[pageid] = dict()
        metadata[pageid] = dict()
        lines = file.readlines()[1:]
        metadata[pageid]['userids'] = map(int,lines[0].strip().split()[2:])
        metadata[pageid]['chars'] = [line.strip().split()[0] for line in lines[1:]]    
        metadata[pageid]['mergetags'] = [cleantag(line.strip().split()[1]) for line in lines[1:]]
        data[pageid].update([(id,map(cleantag,line.strip().split()[2:])) for id,line in zip(count(),lines[1:])])    
        file.close()
    return (data,metadata)

def cleantag(tag):
    split = tag.split('-')
    if len(split) >= 2:
        try:
            return int(split[2])
        except:
            return split[2]
    else:
        return tag

    
if __name__ == "__main__": main()


