pagenodeusertags <- read.table('pagenodeusertags.csv', header=TRUE, sep=",", na.strings=c("none"))

agr_i <- function (coders, categories, n_k) {
    sum_k = 0;   
    n_kvec = as.vector(n_k) 
    c = length(n_kvec) 
    for (k in levels(n_k)) {
        nk = length(n_kvec[n_kvec == k])
        sum_k = sum_k + (nk * (nk-1))
    }
    return ( ( 1/( c * (c-1) ) ) * sum_k )
}

## observed agreement
A_o = NULL;
#A_o <- read.table(file='A_o.csv', sep=",", header=TRUE)
#
categories = NULL
coders = NULL
nodes = NULL

categories = c('1','2','3') 
k = length(categories)
for (pageid in sort(unique(pagenodeusertags$pageid))) {
    coders = unique(pagenodeusertags[pagenodeusertags$pageid == pageid,]$userid)
    c = length(coders)
    nodes = unique(pagenodeusertags[pagenodeusertags$pageid == pageid,]$nodeid)
    i = length(nodes)

    print(pageid)
    #print(c)
    #print(i)

    sum_i = 0
    for (node in nodes) {
        n_ik = as.factor(pagenodeusertags[pagenodeusertags$pageid == pageid & pagenodeusertags$nodeid == node,]$tag)
        sum_i = sum_i + (agr_i(c, categories, n_ik))
    }
    A_o <- rbind(A_o,data.frame(page_id=pageid, A_o=(( 1/i ) * sum_i), nodes=i))
    print(( 1/i ) * sum_i)
}
#write.table(A_o, file='A_o.csv', sep=",")


## extected agreement
A_e = NULL;
#A_e <- read.table(file='A_e.csv', sep=",", header=TRUE)
#
categories = NULL
coders = NULL
nodes = NULL

categories = c('1','2','3') 
k = length(categories)
for (pageid in sort(unique(pagenodeusertags$pageid))) {
    coders = unique(pagenodeusertags[pagenodeusertags$pageid == pageid,]$userid)
    c = length(coders)
    nodes = unique(pagenodeusertags[pagenodeusertags$pageid == pageid,]$nodeid)
    i = length(nodes)

    print(pageid)    
    #print(c)
    #print(i)

    sum_k = 0
    n_k = as.factor(pagenodeusertags[pagenodeusertags$pageid == pageid,]$tag)
    for (k in levels(n_k)) {
        n_kvec = as.vector(n_k)
        c = length(n_kvec)
        for (k in levels(n_k)) {
            nk = length(n_kvec[n_kvec == k])
            sum_k = sum_k + nk^2
        }
    }
    A_e <- rbind(A_e,data.frame(page_id=pageid, A_e=(( 1 / (i * c)^2 ) * sum_k)))
    print(A_e=(( 1 / (i * c)^2 ) * sum_k))
}
# write.table(A_e, file='A_e.csv', sep=",")

agreement = as.data.frame(cbind(page_id=A_o[,1],A_o=A_o[,2],A_e=A_e[,2],nodes=A_o[,3]))
write.table(agreement, file='agreement.csv', sep=",")
#agreement <- read.table('agreement.csv', header=TRUE, sep=",", na.strings=c( "none"))

# coef: (A_o - A_e) / ( 1 - A_e)
agree <- function (A_o, A_e) {
    return ( (A_o-A_e) / (1-A_e) )
}

agreetbl = NULL
num_nodes = sum(agreement$nodes)
for (i in seq(1:nrow(agreement))) {
    A_o = agreement$A_o[i]
    A_e = agreement$A_e[i]
    page = agreement$page_id[i]
    pagenodes = agreement$nodes[i]
    frac = num_nodes/pagenodes

    agreetbl <- rbind(agreetbl,data.frame(page_id=page, agreement=agree(A_o,A_e))) 
    print(paste(page,agree (A_o,A_e) ) )
}

#pdf('./agreementonpages.pdf',7,4)
# hist(agreetbl$agreement, main=NULL,xlab="Inter-Coder Agreement", ylab="Number of Pages", cex.axis = .85, cex.lab = .85, breaks=c(seq(0.3,1,0.1)+0.05))
#dev.off()
