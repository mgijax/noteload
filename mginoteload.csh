#!/bin/csh -f

#
# Wrapper script to create & load mginotes into MGI_Note
#
# Usage:  mginoteload.csh
#

cd `dirname $0`

# DB schema directory; its Configuration file will set up all you need
setenv SCHEMADIR /usr/local/mgi/live/dbutils/mgd/mgddbschema
#setenv SCHEMADIR /home/lec/db/mgddbschema
source ${SCHEMADIR}/Configuration

# Nomen load specific
#setenv NOTELOAD	/usr/local/mgi/dataload/noteload/mginoteload.py
setenv NOTELOAD	/home/lec/loads/noteload/mginoteload.py
setenv NOTEMODE	load
#setenv NOTEMODE	preview

# specific to your load
setenv DATAFILE 	specific to your load
setenv NOTETYPE		"GO Text"
setenv OBJECTTYPE       Marker

setenv LOG `basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}
 
#
# Execute mginoteload
#
${NOTELOAD} -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${OBJECTTYPE} -T\"${NOTETYPE}\" >>& ${LOG}

date >> ${LOG}

