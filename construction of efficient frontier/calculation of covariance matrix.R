rm(list = ls())

require(reshape2)
require(RMySQL)

#Data preperation: read, transform, transpose, and melt
nas_table <- read.csv('NasdaqReturns.csv', sep = ',')
nas_table_mtx <- data.matrix(nas_table)[,-c(1,2,3)]
rownames(nas_table_mtx) <- nas_table[,1]
nas_table_transposed <- t(nas_table_mtx)
cov_nas_table <- cov(nas_table_transposed)
allcov <- melt(cov_nas_table)

#Finding the stocks that has the maximum and minimum variance, so that we could use these two number as the upper and lower bound
#to try out different risk contraints later
stock_var <- c()
for (i in 1:ncol(nas_table_transposed)) {
  stock_var[i] <- var(nas_table_transposed[,i])
}
hist(stock_var, breaks = 500)
stock_var[which.min(stock_var)]
stock_var[which.max(stock_var)]

#Hooking up MySQL
con <- dbConnect(RMySQL::MySQL(), dbname = 'nasdaq', username = 'root', password = 'Mark0401Xuan_')
dbListTables(con)     #Looking up tables

#Batching and inserting first 1340500 rows into the database
ist_into <- "insert into cov values"
k <- 0
l <- 0
for (i in 1:2681) {
  value_vec <- c()
  for (j in 1:500) {
    value_vec <- c(value_vec, sprintf("('%s', '%s', %s)", allcov[j+k,1], allcov[j+k,2], allcov[j+k,3]))
    value_vec_pasted <- paste(value_vec, collapse = ',')
  }
  insert <- paste(ist_into, value_vec_pasted)
  dbSendQuery(con, insert)
  k <- k + 500
  l <- l + 1
  print(paste('Batch', l, 'insert complete.'))
}

#Inserting the remaining 464 rows into the database
additive <- 1340500
value_vec_remainder <- c()
for (i in 1:464) {
  value_vec_remainder <- c(value_vec_remainder, sprintf("('%s', '%s', %s)", 
                                                        allcov[i+additive,1], 
                                                        allcov[i+additive,2], 
                                                        allcov[i+additive,3]))
}
value_vec_pasted_remainder <- paste(value_vec_remainder, collapse = ',')
insert_remainder <- paste(ist_into, value_vec_pasted_remainder)
dbSendQuery(con, insert_remainder)

#Inserting returns into database
monthly_returns <- c()
name_vec <- colnames(nas_table_transposed)
for (i in 1:ncol(nas_table_transposed)) {
  return_insert <- sprintf("insert into ret values ('%s', %s)", name_vec[i], mean(nas_table_transposed[,i]))
  dbSendQuery(con, return_insert)
}
