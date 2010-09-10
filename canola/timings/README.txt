the 3 files annos.csv, pageinfo.csv, subms.csv are dumped from the DB:

wget http://krdwrd.org/db/getannos_csv -O - | gunzip > annos.csv
wget http://krdwrd.org/db/getpageinfos_csv -O - | gunzip > pageinfos.csv
wget http://krdwrd.org/db/getsubms_csv -O - | gunzip > subms.csv
