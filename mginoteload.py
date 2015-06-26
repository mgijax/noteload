#!/usr/local/bin/python

'''
#
# Purpose:
#
#	To load Notes into the MGI Note structures:
#		MGI_Note
#		MGI_NoteChunk
#
# Assumes:
#
#	That no one else is adding Notes to the database.
#
# Side Effects:
#
#	None
#
# Input:
#
#	A tab-delimited file in the format:
#		field 1: MGI ID of MGI Object being Annotated
#		field 2: Notes
#
# Parameters:
#	-S = database server
#	-D = database
#	-U = user
#	-P = password file
#	-M = mode (load, preview)
#	-I = input file
#	-O = object type
#	-T = Note Type (ex. "GO Text")
#
#	processing modes:
#		load - delete all Notes for the given MGI Object Type and Note Type and load the new Notes
#
#		incremental - delete the Notes for the Objects specified in the input file
#
#		preview - perform all record verifications but do not load the data or
#		          make any changes to the database.  used for testing or to preview
#			  the load.
#
# Output:
#
#	1.  BCP file for ALL_Note
#	2.  Diagnostics file of all input parameters and SQL commands
#	3.  Error file
#
# Processing:
#
#	1. Verify the Note Type exists in MGI_NoteType.
#	   If it does not exist, abort the load.
#	   If it does exist, retrieve the _NoteType_key.
#
#	2. Verify Mode.
#		if mode = preview:  set "DEBUG" to True
#
#	For each line in the input file:
#
#	1.  Verify the MGI ID is valid for given Object type.
#	    If the verification fails, report the error and skip the record.
#	    If the verification succeeeds, store the MGI ID/Key pair in a dictionary
#	    for future reference.
#
#	2.  If mode == load, delete all existing Notes of the specified Object Type/Note Type.
#
#	3.  If mode == incremental, delete any existing Notes for the specified Objects/Note Type.
#
#	4.  If mode == load or incremental, bcp the data into the database.
#	
#
# History:
#
# lec	12/11/2014
#	- TR11750/postgres : added logic for postgres version
#
# lec	02/28/2005
#	- created
#
'''

import sys
import os
import string
import re
import getopt
import accessionlib
import mgi_utils
import loadlib
import db

db.setTrace()
db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

#globals

DEBUG = 0		# set DEBUG to false unless preview mode is selected

inputFile = ''		# file descriptor
diagFile = ''		# file descriptor
errorFile = ''		# file descriptor
noteFile = ''		# file descriptor
noteChunkFile = ''	# file descriptor
sqlFile = ''		# file descriptor

diagFileName = ''	# file name
errorFileName = ''	# file name
noteFileName = ''	# file name
noteChunkFileName = ''	# file name
passwordFileName = ''	# file name
sqlFileName = ''	# file name

noteTable = 'MGI_Note'
noteChunkTable = 'MGI_NoteChunk'

mode = ''		# processing mode
noteTypeName = ''	# MGI_NoteType.noteType
noteTypeKey = 0		# MGI_NoteType._NoteType_key
objectTypeKey = ''	# MGI_Note._Object_key
createdByKey = 0
splitfieldDelim = '\t'
fieldDelim = '\t'
lineDelim = '\n'

mgiObjects = {}

loaddate = loadlib.loaddate

def showUsage():
	'''
	# requires:
	#
	# effects:
	# Displays the correct usage of this program and exits
	# with status of 1.
	#
	# returns:
	'''
 
	usage = 'usage: %s -S server\n' % sys.argv[0] + \
		'-D database\n' + \
		'-U user\n' + \
		'-P password file\n' + \
		'-M mode\n' + \
		'-I input file\n' + \
		'-O object type\n' + \
		'-T note type name\n'
	exit(1, usage)
 
def exit(status, message = None):
	'''
	# requires: status, the numeric exit status (integer)
	#           message (string)
	#
	# effects:
	# Print message to stderr and exits
	#
	# returns:
	#
	'''
 
	if message is not None:
		sys.stderr.write('\n' + str(message) + '\n')
 
	try:
		diagFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
		errorFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
		diagFile.close()
		errorFile.close()
	except:
		pass

	sys.exit(status)
 
def init():
	'''
	# requires: 
	#
	# effects: 
	# 1. Processes command line options
	# 2. Initializes local DBMS parameters
	# 3. Initializes global file descriptors/file names
	#
	# returns:
	#
	'''
 
	global inputFile, diagFile, errorFile, errorFileName, diagFileName
	global passwordFileName
	global noteFile, noteFileName, noteChunkFile, noteChunkFileName, sqlFile, sqlFileName
	global mode
	global noteTypeName
	global objectTypeKey, createdByKey
	global mgiObjects
 
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'S:D:U:P:M:I:O:T:')
	except:
		showUsage()
 
	#
	# Set server, database, user, passwords depending on options
	# specified by user.
	#
 
	server = None
	database = None
	user = None
	password = None
 
	for opt in optlist:
                if opt[0] == '-S':
                        server = opt[1]
                elif opt[0] == '-D':
                        database = opt[1]
                elif opt[0] == '-U':
                        user = opt[1]
                elif opt[0] == '-P':
			passwordFileName = opt[1]
                elif opt[0] == '-M':
                        mode = opt[1]
                elif opt[0] == '-I':
                        inputFileName = opt[1]
                elif opt[0] == '-O':
                        objectType = opt[1]
                elif opt[0] == '-T':
                        noteTypeName = re.sub('"', '', opt[1])
                else:
                        showUsage()
 
	# Initialize db.py DBMS parameters
        password = string.strip(open(passwordFileName, 'r').readline())
	db.set_sqlLogin(user, password, server, database)

	db.useOneConnection(1)
 
	fdate = mgi_utils.date('%m%d%Y')	# current date
	head, tail = os.path.split(inputFileName) 

	diagFileName = tail + '.' + fdate + '.diagnostics'
	errorFileName = tail + '.' + fdate + '.error'
	noteFileName = tail + '.' + noteTable + '.bcp'
	noteChunkFileName = tail + '.' + noteChunkTable + '.bcp'
	sqlFileName = tail + '.sql'

	try:
		inputFile = open(inputFileName, 'r')
	except:
		exit(1, 'Could not open file %s\n' % inputFileName)
		
	try:
		diagFile = open(diagFileName, 'w')
	except:
		exit(1, 'Could not open file %s\n' % diagFileName)
		
	try:
		errorFile = open(errorFileName, 'w')
	except:
		exit(1, 'Could not open file %s\n' % errorFileName)
		
	try:
		noteFile = open(noteFileName, 'w')
	except:
		exit(1, 'Could not open file %s\n' % noteFileName)
		
	try:
		noteChunkFile = open(noteChunkFileName, 'w')
	except:
		exit(1, 'Could not open file %s\n' % noteChunkFileName)
		
	try:
		sqlFile = open(sqlFileName, 'w')
	except:
		exit(1, 'Could not open file %s\n' % sqlFileName)
		
	# Set Log File Descriptor
	try:
		db.set_sqlLogFD(diagFile)
	except:
		pass

	diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
	diagFile.write('Server: %s\n' % (server))
	diagFile.write('Database: %s\n' % (database))
	diagFile.write('User: %s\n' % (user))
	diagFile.write('Input File: %s\n' % (inputFileName))
	diagFile.write('Object Type: %s\n' % (objectType))
	diagFile.write('Note Type: %s\n' % (noteTypeName))

	errorFile.write('Start Date/Time: %s\n\n' % (mgi_utils.date()))

	objectTypeKey = accessionlib.get_MGIType_key(objectType)
	createdByKey = loadlib.verifyUser(db.get_sqlUser(), 0, errorFile)

	results = db.sql('select accID, _Object_key from ACC_Accession ' + \
		'where _MGIType_key = %s ' % (objectTypeKey) + \
		'and _LogicalDB_key = 1 ' + \
		'and prefixPart = \'MGI:\' ' + \
		'and preferred = 1', 'auto')
	for r in results:
		mgiObjects[r['accID']] = r['_Object_key']

def verifyNoteType():
	'''
	# requires:
	#
	# effects:
	#	verifies that the Note Type Name exists in the MGI_NoteType table
	#	if it does not exist, an error is written to the error file and the
	#	program is aborted.
	#	if it does exist, the global noteTypeKey is set accordingly
	#
	# returns:
	#	nothing
	#
	'''

	global noteTypeKey

	results = db.sql('select _NoteType_key from MGI_NoteType ' + 
		'where _MGIType_key = %s ' % (objectTypeKey) + \
		'and noteType = \'%s\'' % (noteTypeName), 'auto')

	if len(results) == 0:
		exit(1, 'Invalid Note Type Name: %s\n' % (noteTypeName))
	else:
		noteTypeKey = results[0]['_NoteType_key']

def verifyMode():
	'''
	# requires:
	#
	# effects:
	#	Verifies the processing mode is valid.  If it is not valid,
	#	the program is aborted.
	#	Sets globals based on processing mode.
	#	Deletes data based on processing mode.
	#
	# returns:
	#	nothing
	#
	'''

	global DEBUG

	if mode == 'load':
		DEBUG = 0
		db.sql('delete from MGI_Note where _MGIType_key = %s ' % (objectTypeKey) + \
			'and _NoteType_key = %s' % (noteTypeKey), None)
	elif mode == 'incremental':
		DEBUG = 0
	elif mode == 'preview':
		DEBUG = 1
	else:
		exit(1, 'Invalid Processing Mode:  %s\n' % (mode))

def processFile():
	'''
	# requires:
	#
	# effects:
	#	Reads input file
	#	Verifies and Processes each line in the input file
	#
	# returns:
	#	nothing
	#
	'''

	lineNum = 0

	results = db.sql('select max(_Note_key) + 1 as nextKey from MGI_Note', 'auto')
	noteKey = results[0]['nextKey']

	# For each line in the input file

	for line in inputFile.readlines():

		error = 0
		lineNum = lineNum + 1

		# Split the line into tokens
		tokens = string.split(line[:-1], splitfieldDelim)

		try:
			accID = tokens[0]
			notes = tokens[1]
		except:
			exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

		if mgiObjects.has_key(accID):
			objectKey = mgiObjects[accID]
		else:
			continue
#			exit(1, 'Invalid Accession ID (%d): %s\n' % (lineNum, accID))

		if len(notes) == 0:
		    continue

	        if mode == 'incremental' or mode == 'preview':
		    sqlFile.write('delete from MGI_Note where _MGIType_key = %s ' % (objectTypeKey) + \
			    'and _NoteType_key = %s ' % (noteTypeKey) + \
			    'and _Object_key = %s\ngo\n' % (objectKey))

		newNotes = ''

		if os.environ['DB_TYPE'] == 'postgres':
			newNotes = notes
		else:
			noteTokens = string.split(notes, '\\n')
			for n in noteTokens:
				newNotes = newNotes + n + chr(10)

		noteFile.write('%s' % (noteKey) + fieldDelim + \
			       '%d' % (objectKey) + fieldDelim + \
			       '%d' % (objectTypeKey) + fieldDelim + \
			       '%d' % (noteTypeKey) + fieldDelim + \
			       '%d' % (createdByKey) + fieldDelim + \
			       '%d' % (createdByKey) + fieldDelim + \
			       '%s' % (loaddate) + fieldDelim + \
			       '%s' % (loaddate) + lineDelim)

		# Write notes in chunks of 255
		chunks = [notes[i:i+255] for i in range(0, len(notes), 255)]
		seqNum = 1

		for chunk in chunks:
			# make sure we escacpe these characters
			if os.environ['DB_TYPE'] == 'postgres':
				chunk = chunk.replace('\\', '\\\\')
				chunk = chunk.replace('#', '\#')
				chunk = chunk.replace('?', '\?')
				chunk = chunk.replace('\n', '\\n')

			noteChunkFile.write('%s' % (noteKey) + fieldDelim)
		        noteChunkFile.write('%d' % (seqNum) + fieldDelim)
		        noteChunkFile.write('%s' % (chunk) + fieldDelim)
		        noteChunkFile.write('%d' % (createdByKey) + fieldDelim)
		        noteChunkFile.write('%d' % (createdByKey) + fieldDelim)
		        noteChunkFile.write('%s' % (loaddate) + fieldDelim)
		        noteChunkFile.write('%s' % (loaddate) + lineDelim)
			seqNum = seqNum + 1

		noteKey = noteKey + 1

#	end of "for line in inputFile.readlines():"

def bcpFiles():
	'''
	# requires:
	#
	# effects:
	#	BCPs the data into the database
	#
	# returns:
	#	nothing
	#
	'''

	db.commit()
	db.useOneConnection()

	noteFile.close()
	noteChunkFile.close()
	sqlFile.close()

	if DEBUG:
		return

        if os.environ['DB_TYPE'] == 'postgres':
	    #sqlCmd = 'psql -a -h%s -d%s -U%s --command "%s;"' \
	#	    % (db.get_sqlServer(), db.get_sqlDatabase(), db.get_sqlUser(), sqlFileName)
	    #diagFile.write('%s\n' % sqlCmd)
	    #os.system(sqlCmd)
    
	    bcpNote = 'psql -a -h%s -d%s -U%s --command "\copy mgd.%s from \'%s\' with null as \'\' delimiter as E\'\\t\';"' \
		    % (db.get_sqlServer(), db.get_sqlDatabase(), db.get_sqlUser(), \
		       noteTable, noteFileName, )
	    diagFile.write('%s\n' % bcpNote)
	    os.system(bcpNote)
    
	    bcpNote = 'psql -a -h%s -d%s -U%s --command "\copy mgd.%s from \'%s\' with null as \'\' delimiter as E\'\\t\';"' \
		    % (db.get_sqlServer(), db.get_sqlDatabase(), db.get_sqlUser(), \
		       noteChunkTable, noteChunkFileName, )
	    diagFile.write('%s\n' % bcpNote)
	    os.system(bcpNote)

	else:
	    sqlCmd = 'cat %s | isql -S%s -D%s -U%s -i%s' \
		    % (passwordFileName, db.get_sqlServer(), db.get_sqlDatabase(), db.get_sqlUser(), sqlFileName)
	    diagFile.write('%s\n' % sqlCmd)
	    os.system(sqlCmd)
    
	    bcpNote = 'cat %s | bcp %s..%s in %s -c -t\"%s" -r"%s" -e %s -S%s -U%s >> %s' \
		    % (passwordFileName, db.get_sqlDatabase(), \
	   	    noteTable, noteFileName, fieldDelim, lineDelim, errorFileName, \
		    db.get_sqlServer(), db.get_sqlUser(), diagFileName)
	    diagFile.write('%s\n' % bcpNote)
	    os.system(bcpNote)
    
	    bcpNote = 'cat %s | bcp %s..%s in %s -c -t\"%s" -r"%s" -e %s -S%s -U%s >> %s' \
		    % (passwordFileName, db.get_sqlDatabase(), \
	   	    noteChunkTable, noteChunkFileName, fieldDelim, lineDelim, errorFileName, \
		    db.get_sqlServer(), db.get_sqlUser(), diagFileName)
	    diagFile.write('%s\n' % bcpNote)
	    os.system(bcpNote)

#
# Main
#

init()
verifyNoteType()
verifyMode()
processFile()
bcpFiles()
exit(0)

