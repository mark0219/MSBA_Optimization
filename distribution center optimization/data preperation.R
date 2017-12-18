rm(list = ls())
require(RMySQL)
require(pracma)
require(reshape2)

#Hooking up with DB
con <- dbConnect(RMySQL::MySQL(), dbname = 'optifinal', username = 'root', password = '****')
dbListTables(con)

#Grabbing stuff from DB
query <- dbSendQuery(con, 'select * from ww_dcs')
table_wmdcs <- fetch(query)
query <- dbSendQuery(con, 'select * from ww_stores')
table_wmstores <- fetch(query, n = 4535)

#Check length
length(unique(table_wmdcs$dc_id))
length(unique(table_wmstores$store_id))

#One of the table has a reversed order for lat and lon columns, so rearrange them.
table_wmdcs <- table_wmdcs[,c(1,2,3,4,5,7,6)]

#Build a matrix
dcs_store_mtx <- matrix(NA, nrow = 46, ncol = 4535, 
                        dimnames = list(unique(table_wmdcs$dc_id),
                                        unique(table_wmstores$store_id)))

#Populate the matrix with calculated distances for each unique distribution center and store pair.
for (i in 1:nrow(table_wmdcs)) {
  for (j in 1:nrow(table_wmstores)) {
    
    from <- c(table_wmdcs[i,7], table_wmdcs[i,6])
    to <- c(table_wmstores[j,3], table_wmstores[j,2])
    dis <- haversine(from, to)
    dcs_store_mtx[i,j] <- dis
    
  }
}

#Melt the matrix
dcs_store_mtx_melted <- melt(t(dcs_store_mtx))
dcs_store_mtx_melted <- dcs_store_mtx_melted[,c(2,1,3)]

#Populating db with "batch-and-send" pattern
ist_into <- "insert into ww_mileage values"
k <- 0
l <- 0
for (i in 1:417) {
  value_vec <- c()
  for (j in 1:500) {
    value_vec <- c(value_vec, sprintf("(%s, %s, %s)", 
                                      dcs_store_mtx_melted[j+k,1], 
                                      dcs_store_mtx_melted[j+k,2], 
                                      dcs_store_mtx_melted[j+k,3]))
    value_vec_pasted <- paste(value_vec, collapse = ',')
  }
  insert <- paste(ist_into, value_vec_pasted)
  #dbSendQuery(con, insert)
  k <- k + 500
  l <- l + 1
  print(paste('Batch', l, 'insert complete.'))
}

additive <- 208500
value_vec_remainder <- c()
for (i in 1:110) {
  value_vec_remainder <- c(value_vec_remainder, sprintf("('%s', '%s', %s)", 
                                                        dcs_store_mtx_melted[i+additive,1], 
                                                        dcs_store_mtx_melted[i+additive,2], 
                                                        dcs_store_mtx_melted[i+additive,3]))
}
value_vec_pasted_remainder <- paste(value_vec_remainder, collapse = ',')
insert_remainder <- paste(ist_into, value_vec_pasted_remainder)
#dbSendQuery(con, insert_remainder)















