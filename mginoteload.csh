#!/bin/csh -fx

#
# Wrapper script to create & load notes into MGI_Note
#
# Usage:  mginoteload.csh
#

setenv CONFIGFILE $1


cd `dirname $0`

source ./Configuration
source ${CONFIGFILE}

cd ${NOTEDATADIR}

rm -rf ${NOTELOG}
touch ${NOTELOG}

date >> ${NOTELOG}

${PYTHON} ${NOTELOAD}/mginoteload.py ${NOTELOAD_CMD} -I${NOTEINPUTFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}"

date >> ${NOTELOG}

