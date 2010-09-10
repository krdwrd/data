userpage <- read.table('userpage.csv', header=TRUE, sep=",", na.strings=c("none"))
user <- read.table('user.csv', header=TRUE, sep=",", na.strings=c("none"))
page <- read.table('page.csv', header=TRUE, sep=",", na.strings=c("none"))

#barplot(t(as.matrix(data.frame(user$X2/user$count_tag,user$X1/user$count_tag,user$X3/user$count_tag))),  col=c("#ffff00ff","#ff0000ff","#00ff00ff"), space=.25, names.arg=c(user$userid), cex.names = .85, cex.axis = .85, xlab="User", axes=FALSE, cex.lab = .85)

#pdf('./submsperpage_hist.pdf',7,4)
#hist(page$withmerge_page_userids, xlim=c(0,14), ylim=c(0,100), main=NULL, xlab="Submissions", ylab="Number of Pages", breaks=c(c(0:12)+0.5), cex.axis = .85, cex.lab = .85, col=c('white','white','white','white','lightgray','lightgray','lightgray','lightgray','lightgray','lightgray','lightgray','lightgray'))
#abline(v=4.5)
#dev.off()

# users with high bias rating:
tmp1 = data.frame(userid=user$userid, bias_rating=user$bias_rating/user$count_tag)
bias_rating = tmp1[order(tmp1$bias_rating),]
tmp2 = boxplot(tmp1$bias_rating, plot=FALSE)
one <- subset.data.frame(tmp1 , tmp1$bias_rating %in% tmp2$out)$userid

# user with high differ rating:
tmp1 = data.frame(userid=user$userid, differ_rating=user$differ_rating/user$count_tag)
differ_rating = tmp1[order(tmp1$differ_rating),]
tmp2 = boxplot(tmp1$differ_rating, plot=FALSE)
two <- subset.data.frame(tmp1, tmp1$differ_rating %in% tmp2$out)$userid

# pages with few submissions to merge 
three <- sort(page$withmerge_page_userids)
four <- page[page$withmerge_page_userids %in% c(1,2,3,4),]
four <- four[order(four$withmerge_page_userids),]$pageid

# mean of number of users tagged a page
five <- summary(page$withmerge_page_userids)

# which user/page combinations are awfull...
tmp <- boxplot(userpage$differ_rating, plot=FALSE)
six <- subset.data.frame(userpage, userpage$differ_rating %in% tmp$out)
