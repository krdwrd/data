# we are dealing with this corpus (canola)
corpusid <- 7
# ...and userids < 5 are 'special' - submissions from these users will be discarded
minuserid <- 5
# we got them from the other analysis...
baduserids <- c(14, 31, 34, 73, 74)

# load the CSV files
sif <- file('subms.csv')  
pif <- file('pageinfos.csv') 
aif <- file('annos.csv') 
#
# read the CSV files as tables with column names
# for subm: the time resolution of 1s may lead to multiple 'identical' submits
subm <- unique(read.table(sif, header=TRUE, sep=",", col.names=c("page_id", "user_id", "timestamp")))
pageinfos <- read.table(pif, header=TRUE, sep=",", col.names=c("page_id", "corpus_id", "wclines", "wcwords", "wcbytes"))
annotations <- read.table(aif, header=TRUE, sep=",", col.names=c("page_id", "tags"))

# discard information
# - not in the corpus of interest
# - with too small userid 

# wclines, wcwords, wcbytes: wc output for the text dump of the page
pageinfos <- subset.data.frame(pageinfos, corpus_id == corpusid & page_id %in% subm$page_id & page_id %in% annotations$page_id)
# user_id, timestamp: all submission timestamps for each user
subm <- subset.data.frame(subm, user_id >= minuserid & page_id %in% pageinfos$page_id & page_id %in% annotations$page_id) 
# get rid of bad user
subm <- subset.data.frame(subm, user_id %in% setdiff(subm$user_id,baduserids))
# tags: number of nodes per page (might change to actual annoations...)
annotations <- subset.data.frame(annotations, page_id %in% pageinfos$page_id & page_id %in% subm$page_id)

# this is a hack - but for the time being it serves the purpose:
# - these values come in as strings, hence, they are transformed into a factor
#   (the come as strings because the first entries /are/ strings... hence,
#    we had to get rid of them first!)
# - in the previous step we got rid of NaN values
annotations$tags <- as.integer(annotations$tags)

# add the columns from annotations (number of DOM nodes) to pageinfos
pageinfos <- merge(pageinfos,annotations)

# we will use this list to store a list of lists
# namely: for each user_id a list of submitted pages;
# - the list entries will hold the sum of delta(timestamps) for submitted pages 
subm_time <- list()
subm_sequence <- list()
subm_table <- data.frame()

# the list with the relevant user_ids and page_ids
users <- data.frame(user_id = unique(subm$user_id))
pages <- pageinfos$page_id 

# sum up the submission times for the users, i.e. for each user
#  1. compute delta(submission1, submission2)
#  2. add the value to the submission time for submission1
for (user_id in users$user_id)
{ 
    last_page <- 0 
    last_timestamp <- 0 

    subm_time[[user_id]] <- list()
    for (timestamp in unique(sort(subm$timestamp[subm$user_id == user_id])))
    {
        # dunno exactly how but there /can/ be multiple entries for
        # /one/ 'user, timestamp' combination - hence, consider them  
        for (page in subm$page_id[subm$user_id == user_id & subm$timestamp == timestamp])
        {
            # initialize value but also
            # make sure not to run 'out of bound'
            tryCatch(subm_time[[user_id]][[page]], error = subm_time[[user_id]][[page]] <- 0)
            if (last_page > 0 && last_timestamp > 0)
            {
                delta = timestamp - last_timestamp
                
                # reorder the sequence - if apropriate, i.e.
                # in case the last visit was shorter than the curent one
                # consier the page /now/ for the sequence in which the user
                # tagged the pages
                if (delta > subm_time[[user_id]][[page]]) {

                    tryval <- try(subm_sequence[[user_id]],silent=TRUE)
                    if (tryCatch(!is.null(subm_sequence[[user_id]]), error = function(x) FALSE)) {
                        # leave out elements with the same page_id and re-combine
                        # the sequence
                        subm_sequence[[user_id]] <- c(subm_sequence[[user_id]][subm_sequence[[user_id]] != page], page)
                    } else {
                        subm_sequence[[user_id]] <- c(page)
                    }
                }
                subm_time[[user_id]][[page]] = subm_time[[user_id]][[page]] + delta 
            } else if (tryCatch(is.null(subm_sequence[[user_id]]), error = function(x) TRUE))
            {
                subm_sequence[[user_id]] <- c(page)
            } 
        }
        last_page <- page
        last_timestamp <- timestamp
    }
}

# build up /one/ big table with all page_ids|user_ids|sequence|times
for (user_id in users$user_id)
{
    for (page_id in subm_sequence[[user_id]])
    {
        val <- tryCatch(subm_time[[user_id]][[page_id]], error = function(err) val <- 1)

        if (val > -1) {
            
            page_seq <- 1
            time <- NaN
            if (val > 0)
            {
                time <- val
                page_seq <- which(subm_sequence[[user_id]] == page_id)
            }
            subm_table <- rbind(subm_table,data.frame(page_id=page_id,user_id=user_id,page_seq=page_seq,time=time))
        }
    }
}

# compute reasonable upper bound for how log a submit action might take, i.e.
# hypothesis: longer times than X were breaks
# furthermore: if a submit took longer discard all submits for the particular page
#  (i.e. the summed timestamps for the page - we cannot know how long much of the
#   break might have been used for actually doing something)
h <- 1.5 * IQR(unlist(subm_time)[unlist(subm_time) > 0])
max_delta_submit <- h + quantile(unlist(subm_time)[unlist(subm_time) > 0], 0.75) 
# use max_delta and reduce the set
subm_delta_table <- subset.data.frame(subm_table, time < max_delta_submit)
#
tmp <- aggregate(subm_delta_table$time, list(subm_delta_table$page_id), FUN=function(x) {mean(x)})
names(tmp) <- c('page_id','t_mean')
pageinfos <- merge(pageinfos,tmp)
#
tmp <- aggregate(subm_delta_table$time, list(subm_delta_table$page_id), FUN=function(x) {median(x)})
names(tmp) <- c('page_id','t_median')
pageinfos <- merge(pageinfos,tmp)
#
tmp <- aggregate(subm_table$user_id, list(subm_table$page_id), FUN=function(x) {length(unique(x))})
names(tmp) <- c('page_id','num_tagged')
pageinfos <- merge(pageinfos,tmp)


tmp <- aggregate(subm_delta_table$time, list(subm_delta_table$user_id), FUN=function(x) {sum(x)})
names(tmp) <- c('user_id','t_sum')
users <- merge(users,tmp)

others <- data.frame() 
num_tagged <- data.frame()
for (user_id in users$user_id)
{
    others_page_mean <- NULL
    others_page_sum <- NULL
    for (page_id in subm_delta_table[subm_delta_table$user_id == user_id,]$page_id) 
    {
        others_page_mean <- c(others_page_mean, mean(subm_delta_table[subm_delta_table$page_id == page_id & subm_delta_table$user_id != user_id,]$time))
        others_page_sum <- c(others_page_sum, mean(subm_delta_table[subm_delta_table$page_id == page_id & subm_delta_table$user_id != user_id,]$time))
    }
    others <- rbind(others, data.frame(user_id=user_id, others_sum=sum(others_page_sum, na.rm=TRUE), others_mean=mean(others_page_mean, na.rm=TRUE)))
    num_tagged <- rbind(num_tagged, data.frame(user_id=user_id, num_tagged=length(subm_sequence[[user_id]])))
}
users <- merge(users,merge(others,num_tagged))


#
#
# testing begins here...
########################

seq_sum <- NULL
seq_mean <- NULL
seq_diff <- NULL
for (page_seq in sort(unique(subm_delta_table$page_seq)))
{
    # 1-51
    others_page_mean <- NULL
    subms_page_mean <- NULL
    delta_page_mean <- NULL
    for (page_id in subm_delta_table[subm_delta_table$page_seq == page_seq,]$page_id) 
    {
        # page_seq = 1
        # e.g. 687 907 817 920 833 870 752 772 734 861
        if (nrow(subm_delta_table[subm_delta_table$page_id == page_id & subm_delta_table$page_seq > page_seq,]) > 1)
        {
            others_page_mean_tmp <- median(subm_delta_table[subm_delta_table$page_id == page_id & subm_delta_table$page_seq > page_seq,]$time, na.rm=TRUE)
            others_page_mean <- c(others_page_mean, others_page_mean_tmp)
        }
        subms_page_mean_tmp  <- median(subm_delta_table[subm_delta_table$page_id == page_id & subm_delta_table$page_seq == page_seq,]$time, na.rm = TRUE)
        subms_page_mean  <- c(subms_page_mean,  subms_page_mean_tmp)

        delta_page_mean <- c(delta_page_mean, subms_page_mean_tmp - others_page_mean_tmp)
    }
    seq_sum <- rbind(seq_sum, data.frame(subms=sum(subms_page_mean),others=sum(others_page_mean)))
    seq_mean <- rbind(seq_mean, data.frame(subms=mean(subms_page_mean, na.rm = TRUE),others=mean(others_page_mean, na.rm = TRUE)))
    seq_diff <- rbind(seq_diff, data.frame(diff=median(delta_page_mean)))  
}

# make plots
#
#pdf('./timespentonassignment.pdf',7,4)
#hist(users$t_sum/60,ylim=c(0,25),breaks=c(seq(1,150,20)+10),main=NULL,xlab="Minutes spent on Assignment", ylab="Number of Users", cex.axis = .85, cex.lab = .85)
#dev.off()

#pdf('./timespentonpage.pdf',7,4)
#boxplot((users$t_sum/users$num_tagged)/60, outline=FALSE, horizontal=TRUE, cex.axi s = .85, cex.lab = .85, main=NULL, xlab='Minutes spent on Page')
#dev.off()

#pdf('./sequencedelta.pdf',4,3)
#plot(loess.smooth(seq(2:15),(seq_diff$diff[2:15])), type='l', main=NULL,xlab="Sequence Position", ylab="Delta in s", cex.axis = .85, cex.lab = .85)
#dev.off()

# how many users y tagged x number of pages
#pdf('./pagesperuser.pdf',7,3)
#barplot(aggregate(subm_table$user_id, list(subm_table$page_seq), length)$x, names.arg=unique(sort((unlist(list(subm_table$page_seq))))), cex.names = .85, cex.axis = .85, cex.lab = .85, space = .1, ylim = c(0,70), xlab='Number of processed Pages', ylab='Number of Users')
#dev.off()
#

# for corpus: 5
#pdf('./timespentontutorial.pdf',7,4)
#hist((users$t_sum[users$t_sum > 420])/60,ylim=c(0,25),breaks=c(seq(0,50,10)+5),main=NULL,xlab="Minutes spent on Tutorial", ylab="Number of Users", cex.axis = .85, cex.lab = .85)
#dev.off()

# how many submissions are there
#nrow(subm) 
#
# how many are unique, 
# i.e. count multiple submissions per user for the same page only once
#tmp <- data.frame(subm$user_id,subm$page_id)
#nrow(unique(tmp[order((tmp)$subm.user_id,(tmp)$subm.page_id),]))

# how did users tag when they were still unexperienced compared to the others
#plot(loess.smooth(seq(1,24),seq_mean$subms[2:25]), type='l',, ylim=c(100,250))
#lines(loess.smooth(seq(1,24),seq_mean$others[2:25]),  type='l', col = 'lightgrey')
#lines(loess.smooth(seq(1,24),(seq_mean$others[2:25]+seq_mean$subms[2:25])/2),  type='l', col = 'darkgrey')

# how were users relative to the set of (others who tagged the same page)
# minus: user was faster than avg.
# barplot(users$t_sum-users$others_sum, names.arg=users$user_id, cex.names = .75)

# which pages took the longest?
# barplot(pageinfos$t_mean, names.arg=pageinfos$page_id, xlab='page_id',ylab='time in s')

# which pages took exceptionally long (within the reduces set...)
#tmp = boxplot(pageinfos$t_mean)
#subset.data.frame(pageinfos, pageinfos$t_mean %in% tmp$out)$page_id

# how long did it take people to tag their share (in s ; divide by 3600 for h)? 
#tmp<- boxplot(aggregate(users$t_sum, list(users$user_id), sum)$x, ylab='total time in h')
# how many outliers
#subset.data.frame(users, users$t_sum %in% tmp$out)

# which 10 pages took the longest
#tail(pageinfos[order(pageinfos$t_mean),], n=10)

#hist(durations, xlab='duration in s')
#
## sane submission boundaries, i.e.
## submissions /that/ fast or /that/ slow seem 'really' strange 
#
#plot(density(durations[ind1 & upper]),log='x',ylim=c(0.001,0.005))
#hist(durations[ind1 & upper], xlab='duration in s')
#hist(durations[ind1 & upper]/60, xlab='duration in min')
#boxplot(durations[ind1 & upper], range=0, log='y', ylab='duration in s')
#
#boxplot(statistics$total_pagetime/60, ylab='minutes', outline=FALSE)
