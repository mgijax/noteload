#!/bin/csh -f

#
# Wrapper script to delete & reload GO Text Notes into MGI_Note
#
# Usage:  gotextload.csh
#

cd `dirname $0` && source ./Configuration

setenv NOTEMODE		load
setenv NOTEINPUTFILE 	/data/loads/go/gotext/input/gotext.txt
setenv NOTETYPE		"GO Text"
setenv NOTEOBJECTTYPE   Marker

setenv LOG /data/loads/go/gotext/logs/`basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}
 
#
# Execute mginoteload
#
cd /data/loads/go/gotext/output
${NOTELOAD} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -I${NOTEINPUTFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" >>& ${LOG}

date >> ${LOG}

