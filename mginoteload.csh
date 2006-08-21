#!/bin/csh -f

#
# Wrapper script to create & load mginotes into MGI_Note
#
# Usage:  mginoteload.csh
#

cd `dirname $0` && source ./Configuration

setenv NOTEMODE		load
setenv NOTEINPUTFILE 	specific to your load
setenv NOTETYPE		"GO Text"
setenv NOTEOBJECTTYPE   Marker

setenv LOG `basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}
 
#
# Execute mginoteload
#
${NOTELOAD} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -I${NOTEINPUTFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T\"${NOTETYPE}\" >>& ${LOG}

date >> ${LOG}

