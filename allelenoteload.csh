#!/bin/csh -f

#
# Wrapper script to create & load allelenotes into MGI_Note
#
# Usage:  allelenoteload.csh
#

cd `dirname $0`

# DB schema directory; its Configuration file will set up all you need
setenv SCHEMADIR /usr/local/mgi/dbutils/mgd/mgddbschema
#setenv SCHEMADIR /home/lec/db/mgi2.98/mgddbschema
source ${SCHEMADIR}/Configuration

# Nomen load specific
#setenv NOTELOAD	/usr/local/mgi/dataload/noteload/allelenoteload.py
setenv NOTELOAD	/home/lec/loads/noteload/allelenoteload.py
setenv NOTEMODE	load
#setenv NOTEMODE	preview

# specific to your load
#setenv DATADIR		specifictoyourload
setenv DATAFILE 	QTLAlleleDef_Load.txt
setenv NOTETYPE		"Molecular"

setenv LOG `basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}
 
#
# Execute allelenoteload
#
${NOTELOAD} -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -T\"${NOTETYPE}\" >>& ${LOG}

date >> ${LOG}

