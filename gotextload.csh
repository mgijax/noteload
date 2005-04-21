#!/bin/csh -f

#
# Wrapper script to delete & reload GO Text Notes into MGI_Note
#
# Usage:  mginoteload.csh
#

cd `dirname $0`

# DB schema directory; its Configuration file will set up all you need
setenv SCHEMADIR /home/lec/db/live/mgddbschema
source ${SCHEMADIR}/Configuration

# Nomen load specific
setenv NOTELOAD	/usr/local/mgi/live/dataload/noteload/mginoteload.py
setenv NOTEMODE	load

# specific to your load
setenv DATAFILE 	/data/loads/go/gotext/input/gotext.txt
setenv NOTETYPE		"GO Text"
setenv OBJECTTYPE       Marker

setenv LOG /data/loads/go/gotext/logs/`basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}
 
#
# Execute mginoteload
#
cd /data/loads/go/gotext/output
${NOTELOAD} -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${OBJECTTYPE} -T"${NOTETYPE}" >>& ${LOG}

date >> ${LOG}

