######!/usr/bin/env python
# -*- coding: utf8 -*-
# coding: utf8

# Copyright (c) 2020 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
	!---------------------------------------------------------!
	!                                                         !
	!                   Vtopo to Therion                      !
	!                                                         !
	!           Code to transform the .tro files              !
	!            Visual Topo into files that can              !
	!                  be used by Therion                     !
	!                                                         !
	!         Based on Xavier Robert pytherion code           !
	!        Simplified and modified by Phil Vernant          !
	!                                                         !
	!---------------------------------------------------------!

	 ENGLISH :
	 Convert Visualtopo .tro file (http://vtopo.free.fr/) into files that can be read 
	 by Therion (http://therion.speleo.sk/).
	 It needs at least the .tro file to run and will produce one .th file (file with survey data),
	 and one thconfig file (file that is used to compile and build the survey with Therion).

	 FRANCAIS :
	 Conversion d'un fichier Visualtopo .tro (http://vtopo.free.fr/) en fichiers Therion
	 (http://therion.speleo.sk/).
	 Il faut à minima un fichier .tro en entrée et il y aura un fichier .th (données topo)
	 et un fichier .thconfig qui permettra d'exécuter therion.  
	 
"""
# Do divisions with Reals, not with integers
# Must be at the beginning of the file
from __future__ import division
#from __future__ import unicode_literals
import sys, os
import unidecode
import numpy as np


def tro2th(fle_tro_fnme = None, cavename = None, 
			xviscale = 1000, xvigrid = 10, scale = 500):
	
	"""
		Main function to convert tro to th files. 
		This is this function that should be called from python.
	
		INPUTS:
			fle_tro_fnme : (string) Path and name of the .tro file to convert. 
			               if None (value by default), the function does not convert anything 
			               but build .thconfig and config.thc files
			               If the path is not given, the function will look in the folder from where it is launched
			cavename     : (string) Name of the cave. 
			               If set to None (default value), it is get from the .tro file.
			xviscale     : (Real) Scale of the xvi file. 
			                Set to 1000 by default that corresponds to 1/1000 
			xvigrid      : (Real) Spacing of the grid for the xvi, in meters. 
			               Set 10 by default
			scale        : (Real) scale of the map
			               Set to 500 by default that corresponds to 1/500 	



			fle_th_fnme  : (string) Path and name of the .th file to create from the .tro file. 
			               If None (value by default), this file is created from the .tro file name 
			               and in the same folder than that .tro file
			thlang       : (string) String that set the language. 'fr' by default. 
			               If you need english, change 'fr' to 'en' in the function definition
			              set 'fr' for french
			              set 'en' for english
			              ... other languages are not implemented
			icomments    : (Boolean) To add (True, by default) or not (False) comments in the produced files
			icoupe       : (Boolean) To set (True, by default) or not (False) an extended-elevation layout in the .thconfig file
			ithconfig    : (Boolean) To set if the thconfig file is created (True, by default) or not 
			thconfigfnme : (string) Path and name of the thconfig file. 
			               If None (by default), path and name build from the .tro file
			ithc         : (Boolean) To build (True, by default) or not (False) a config file config.thc 
			thcpath      : (string) Path to the directry that contains the config file called in the cave.thconfig file.
			                If used with ithc = False, this path is only used for the declaration 
			                in the cave.thconfig
			                If used with ithc = True, the config file will be written in that directory.
			                Set to None by default
			thcfnme      : (string) Name of the config.thc (value by default if set to None or if ommitted)
			sourcefile   : (list of strings) Define the source files declared in the cave.thconfig
							ex :['example.th', 'example.th2', 'example-coupe.th2']
							If None or ommitted, it is build from the .tro file or the cavename
			Errorfiles   : (Boolean) If True (by default), an error will be raised if output files exists in the folder
			               If False, only a warning is raised, and the previous files are erased by the new ones.
			               Use with caution
			
		OUTPUTS:
			cavename.th       : survey data for Therion
			cavename.thconfig : file to run Therion and build the pdf's maps and others
			
		USAGE:
			To run with only the .tro file
			tro2th(fle_tro_fnme = 'file.tro')

			To run with all the options .tro file
			tro2th(fle_tro_fnme = 'file.tro', cavename = 'Test',
			       xviscale = 1000, xvigrid = 10, scale = 500)
					
		Author: Modified by Phil Vernant from Xavier Robert'Pytherion 2022/02
		
		Licence: CCby-nc
	"""
	
	print(u'____________________________________________________________\n\n\t\t\tVtopo2therion\n____________________________________________________________\n')
	print(u'\nModified by Phil Vernant from Xavier Robert\'s Pytherion\nVersion 2022/02\n')
	print(u'____________________________________________________________\n\n')
	
	coordsyst = None		
	if fle_tro_fnme is not None:
		if fle_tro_fnme[-4:] != u'.tro':
			fle_tro_fnme = fle_tro_fnme + u'.tro'
		# check if file exists
		if os.path.isfile(fle_tro_fnme) == False :
			raise NameError(u'ERROR : FR : Le fichier {FileNa} n\'existe pas'.format(FileNa=str(fle_tro_fnme)))
			raise NameError(u'ERROR : EN : Cannot find {FileNa}'.format(FileNa=str(fle_tro_fnme)))
		

		# convert tro file to th file
		cavename, coordsyst, fle_th_fnme = convert_tro(fle_tro_fnme)
		
		print(u'\tFR : Fichier Therion %s construit à partir des données %s' %(fle_th_fnme, fle_tro_fnme))
		print(u'\tEN : File %s created from %s\n' %(fle_th_fnme, fle_tro_fnme))
	else:
		print(u'\tFR : Pas de fichier .tro en entrée, pas de fichier .th créé...')
		print(u'\tEN : No .tro File input, no .th file created...')

	sourcefile = [fle_th_fnme.lower(), u'#' + fle_th_fnme[0:-4].lower() + u'.th2', u'#' + fle_th_fnme[0:-4].lower() + u'-coupe.th2' ]
	# Build the dictionnary for the thconfig file	
	dictcave = [sourcefile, xviscale, xvigrid, cavename, coordsyst, scale, cavename.lower().replace(u' ', u'_').replace(u'\'', u'_')]

	# build thconfig file
	thconfigfnme = cavename.lower().replace(u' ', u'_').replace(u'\'', u'_') + u'.thconfig'
	writethconfig(thconfigfnme, dictcave)
	print(u'____________________________________________________________')
	print(u'')
	
	return
	

	
def convert_tro(fle_tro_fnme, cavename = None):	
	"""
		Function that manages the tro 2 th conversion
		
		INPUTS:
			fle_tro_fnme : path and file name of the .tro file to convert
			cavename     : Name of the cave. If ommitted, it is set to None, and it is get from the .tro file 

		OUTPUTS:
			new .th file with surveyed data for Therion
			cavename      : Name of the cave from the .tro file
			coordsyst     : Coordinates system used by the .tro file
			
		USAGE:
			cavename, coordsyst = convert_tro(fle_tro_fnme, [cavename = cavename])
			          cavename can be ommitted.
		
		Author: Xavier Robert, Lima 2016/06/27
		Modif : Phil Vernant, 2022/02/16
		
		Licence: CCby-nc
	"""
	
	#from codecs import open
		
	# Initialization of some variables...
	#xcoord=0.
	#ycoord=0.
	#alt=0.
	
	# open the .tro survey	
	print(u'\tFR : Travail sur %s' % fle_tro_fnme)
	print(u'\tEN : Processing %s' % fle_tro_fnme)
	print(' ')
	fle_tro = open(fle_tro_fnme, 'rU', encoding='latin-1')                                  
	# read the .tro file
	lines = fle_tro.readlines()
	
	# read the header
	cavename, coordinates, coordsyst, club, entrance, versionfle = read_vtopo_header(lines)
	
	if cavename is None or cavename == '' or cavename == ' ':
		cavename = u'cave'
	
	# create .th file name 
	fle_th_fnme = cavename.lower().replace(u' ', u'_').replace(u'\'', u'_') + u'.th'
	
	# check if file exists... !!! existing therion files will be overwritten
	checkfiles(fle_th_fnme)
	# open the .th file

	fle_th = open (fle_th_fnme, 'w')
	# write the .th header
	writeheader_th(fle_th, cavename, entrance)
	
	# initiate variables
	i = 0
	iline = []
	dataold = []
	
	# get line numbers of the lines beginning with 'Param'
	for line in lines:
		if u'Param' in line: iline.append(i)
		i+=1
	
	for j in iline:
		# read the settings of the survey
		settings, comments = read_settings(lines[j].replace(u'\n', u''))
		print(settings)
		# read the data from the tro file
		data = read_data(lines, settings, j, iline)
		
		# write centerline header
		writecenterlineheader(fle_th, entrance, settings, comments, data, coordsyst, coordinates, club)

		# write the data to the .th file
		writedata(fle_th, settings, data, dataold)
		
		# write the end of the centerline in the .th file
		fle_th.write(u'\n\tendcenterline\n\n')
		dataold = data	
	# write the end of the survey in the .th file
	fle_th.write(u'\nendsurvey\n')
	fle_th.close
		
	print (u'\tFR : Fichier %s écrit !' % fle_th_fnme.lower())
	print (u'\tEN : File %s written!\n' % fle_th_fnme.lower())
	
	return cavename, coordsyst, fle_th_fnme

# vtopotools

def read_vtopo_header(lines):
	"""
		Function to read header from vtopofile
		
		INPUTS:
			lines: file .tro read by the fonction lines = readlines(file_vtopo)
		
		OUTPUTS (all are strings):
			cavename    : Name of the cave
			coordinates : Entrance coordinates
			coordsyst   : Coordinates system to set the entrance coordinates
			club        : Name of the group that explored the cave
			entrance    : Entrance of the cave
			versionfle  : Vtopo version that has been used to produce the vtopofile
		
		USAGE:
			cavename, coordinates, coordsyst, club, entrance, versionfle = read_vtopo_header(lines)
				
		Author: Xavier Robert, Lima 2016/06/27
		modif : Phil Vernant 2022/02/08
		
		Licence: CCby-nc
	"""
	
	# coord_dict: French Lambert system. To find number of your system, see extern/proj4/nad/epsg 
	#             file in the therion source distribution. You can add your own lines/systems
	coord_dict = {u'LT1' : u'EPSG:27571',
	             u'LT2' : u'EPSG:27572',
	             u'LT3' : u'EPSG:27573',
	             u'LT4' : u'EPSG:27574',
	             u'LT9' : u'EPSG:2154'
	             }

	club = None
	
	for line in lines:
		if u"Version" in line:
			versionfle = line[1].replace(u'\n', u'').rstrip(u'\n\r').split(' ')
		if u'Trou' in line[0:20]:
			# read Trou
			(cavename, xcoord, ycoord, alt, coordtro) = line[5:].replace(u'\n', u'').rstrip(u'\n\r').split(u',')
			cavename = unidecode.unidecode(cavename)
			coordinates = [xcoord, ycoord, alt]
		# read club
#		if u'Club' in line: club = line[5:].replace(u'\n', u'')
		if u'Club' in line: 
			if len(line[5:].replace(u'\n', u'').split(u' ')) < 3 : club = line[5:].replace(u'\n', u'')
			if len(line[5:].replace(u'\n', u'').split(u' ')) > 2 : club = line[5:].replace(u'\n', u'').replace(u' ', u'-')
			
		# read entrance name
		if u'Entree' in line : entrance = line[7:].replace(u'\n', u'')
	
	if coordtro[:3] in coord_dict:
		# Rewrite the coordinate system to be read by Therion
		# French Lambert system. To find number of your system, see extern/proj4/nad/epsg file in the therion source distribution. You can add you own lines/systems
		coordsyst = coord_dict[coordtro[0:3]]
		# make sure the coordinates are in meters
		if float(coordinates[0]) < 20000 :
			 coordinates[0] = float(coordinates[0])*1000
			 coordinates[1] = float(coordinates[1])*1000
	else:
		coordsyst = None
	
	return cavename, coordinates, coordsyst, club, entrance, versionfle

	
def read_settings(line):
	"""
		Function to read the line that define the settings of the survey session : 
		  intruments, directions, units, calibrations,...
		
		INPUTS:
			line     : string extractd from the .tro file that contains the information on the survey session
			
		OUTPUTS:
			settings : list of strings with all the measurments settings
			comments : string that correspond to the end of the string "Line" 
			           that do not correspond to the settings
		USAGE:
			settings, comments = read_settings(line)
			          
		Author: Xavier Robert, Lima 2016/06/27
		
		Licence: CCby-nc
	"""
	# Question: Do we have to update the code in function of the vtopo version number?
	param = line[6:].rstrip(u'\n\r').split(u' ')
	k = 8
	#k = 6
	if 'Topof' in param[:k]:
		k = k + 1
	if 'Prof' in param[:k] or 'Deniv' in param[:k]: 
		k = k - 1
	settings = param[:k]
	#commentst = param[k+2:]
	commentst = param[k:]
	comments = " ".join(str(elem)  for elem in commentst)
	
	#ucomments=comments.decode('us-ascii', errors = 'replace')
	#print ucomments
	
	return settings, comments#.encode('utf-8', errors = "replace")


def read_data(lines, settings, j, iline):
	"""
		Function to read the data from the line
		
		INPUTS:
			lines    : file .tro read by the fonction lines = readlines(file_vtopo)
			settings : list of strings with all the measurments settings;
			           output of the function read_settings
			j        : number of the line that corresponds to the settings line in the list "lines"
			iline    : list of line numbers that correspond to the different settings line in the list "lines"
		
		OUTPUTS:
			data     : list of lists of data (string format)

		USAGE:
			data = read_data(lines, settings, j, iline)
				
		Author: Xavier Robert, Lima 2016/06/27
		
		Licence: CCby-nc
	"""
	
	data = []
	# check if we are at the end of the iline file or not !
	if iline.index(j) < len(iline)-1:
		for i in range(j+1, iline[iline.index(j)+1]):
 			datal = [x for x in lines[i].replace(u'\n', u'').rstrip(u'\n\r').split(u' ') if x != u'']
 			data.append(datal)
	else:
		i = j+1
		while 1:
 			if 'Configuration' in lines[i]:
 				break
 			else:
 				datal = [x for x in lines[i].replace(u'\n', u'').rstrip('\n\r').split(u' ') if x != u'']
	 			data.append(datal)
 				i+=1
	# remove white lines in datao
	data = [x for x in data if x != []]
	
	return data

# datawritetols
def writeheader_th(file, cavename, entrance):
	"""
	Function to write the header of the file.th
	
	INPUTS:
	   file     : variable that sets the file.th
	   cavename : name of the cave
	   entrance : name of the entrance station
	   
	OUTPUTS:
		None
		
	USAGE:
		writeheader_th(file, cavename, entrance)
		
	Author: Xavier Robert, Lima 2016/06/27
	
	Licence: CCby-nc
	
	"""
	
	file.write(u'encoding utf-8 \n\nsurvey %s -title "%s" -entrance "%s" \n'
	           %(cavename.replace(u' ', u'_').replace(u'\'', u'_'), cavename, entrance))
	
	return


def writecenterlineheader(file, entrance, settings, comments, data, coordsyst, coordinates, club):
	"""
	Function to write the centerline header
	
	
	INPUTS:
		file        : variable that sets the file.th
		entrance    : name of the entrance station
		settings    : List of the settings of this survey section
		comments    : String that correspond to the end of the string "Line" 
		              that do not correspond to the settings
		data        : data from this survey section
		coordsyst   : Coordinates system to set the entrance coordinates
		coordinates : Entrance coordinates
		club        : Name of the group that explored the cave
	   
	OUTPUTS:
		None
		
	USAGE:
		writeheader_th(file, cavename, entrance)
		
	Author: Xavier Robert, Lima 2016/06/27
	Modif : Phil Vernant Feb 2022
	"""
	# First, define dictionaries to help the coding
	# angleU: define the angle unit
	angleU = {u'Deg' : u'degrees',
	          u'Degd' :u'degrees',
	          u'Gra' : u'grad'}
	# compassdir:
	dir = {u'Dir' : u'',
	       u'Inv' : u'back'}
	# lruddir: Set the LRUD
	lruddir = {u'Dir' : u'left right up down',
	           u'Inv' : u'right left up down',
	           u'Nod' : u''}
	# unitcounter: set the unit of the counter (for the length)
	unitcounter = {u'Vulc' : u'centi',
	               u'Prof' : u'',
	               u'Deniv': u''}
	# unitclino: used to correct the clino if topoVulcain
	unitclino = {u'Deg'  : u'90',
	             u'Degd' : u'90',
	             u'Gra'  : u'100'}
	# typelen: type of length measures
	typelem = {u'Deca' : u'normal',
	          u'Topof' : u'topofil',
	          u'Vulc' : u'topofil',
	          u'Prof' : u'diving',
	          u'Deniv' : u'deniv'}
	# style: data style
	style = {u'Deca'   : u'normal',
	         u'Topof'  : u'topofil',
	         u'Diving' : u'diving',
	         u'Prof'   : u'diving',
	         u'Carth'  : u'carthesian',
	         u'Cylp'   : u'cylpolar',
	         u'Dim'    : u'dimensions',
	         u'Nosy'   : u'nosurvey'} 
	# station: type of stations
	station = {u'station' : u'station',
	           u'from'    : u'from',
	           u'to'      : u'to',
	           u'vtopo'   : u'from to'}
	# lensurv: how are set the length measurements
	lensurv = {u'Deca'   : u'length',
	           u'Topof'  : u'fromcount tocount',
	           u'Diving' : u'length',
	           u'Prof'   : u'length'}
	# slopesurv: how are set the slope measurements
	slopesurv = {u'Clino' : u'clino',
	             u'Vulc'  : u'clino',
	             u'Deniv' : u'depthchange',
	             u'Prof'  : u'depthchange'}	             # changed form depth to depth change to avoid interleaved data format and associated to depth change computation for data
    
    # Begin the centerline
	file.write(u'\n\tcenterline \n')
	
	# if entrance in the data, write the entrance coordinates
	if [datal for datal in data if entrance in datal] != []:
		if coordsyst != None:
			file.write(u'\t\tcs %s \n' 
		               u'\t\tfix %s %s %s %s \n\n' % (coordsyst, entrance, coordinates[0], coordinates[1], coordinates[2])) 
		else:
			file.write(u'\t\t#cs %s \n' 
		               u'\t\t#fix %s %s %s %s \n\n' % (coordsyst, entrance, coordinates[0], coordinates[1], coordinates[2])) 
	typem = u'Deca'
	
	if u'Topof' not in settings:             
		settings [1:1]= u' '
#		typem = u'Topof'
	if u'Prof' in settings or u'Deniv' in settings:
		settings[4:4] = u' '
	# next line used to debug
	#file.write(u'\t' + str(settings) + u'\n')
	# write the survey caracteristics
	file.write(u'\t\t#date YYYY.MM.DD \n')

	file.write(u'\t\tdeclination %s %s \n'% (str([string for string in settings if '.' in string][0]), angleU[settings[2]]))
	if club != None:
		file.write(u'\t\tteam "%s" \n' % club)
	
	dirs = settings[6].rstrip(u'\n\r').split(u',')
	
	file.write(u'\n\t\tunits length meters \n')
	if u'Topof' in settings:
		file.write(u'\t\tunits counter %smeters \n' % unitcounter[settings[3]])
		file.write(u'\t\tcalibrate counter 0 %s \n' % settings[1])
		# To set the slope
	if u'Vulc' in settings:
		file.write(u'\t\tcalibrate clino %s -1\n' % unitclino[settings[4]])
	if u'Prof' in settings:
		file.write(u'\t\tunits depth meters \n')
		typem = u'Prof'
	elif u'Deniv' in settings:
		file.write(u'\t\tunits depth meters \n')
		typem = u'Diving'
	
	file.write(u'\t\tunits compass %s \n' % (angleU[settings[2]]))
	if u'Vulc' in settings or 'Clino' in settings:
		file.write(u'\t\tunits clino %s \n' % (angleU[settings[4]]))
	
	if u'depth' not in slopesurv[settings[3]]:
		file.write(u'\n\t\tdata %s %s %s %scompass %s%s %s\n' 
	           % (style[typem], station[u'vtopo'], lensurv[settings[0]], 
	              dir[dirs[0]], dir[dirs[1]], slopesurv[settings[3]],
	              lruddir[dirs[2]]))
	else:
		file.write(u'\n\t\tdata %s %s %s %scompass %s %s\n' 
	           % (style[typem], station[u'vtopo'], lensurv[settings[0]], 
	              dir[dirs[0]], slopesurv[settings[3]],
	              lruddir[dirs[2]]))
	              	
	if comments != u'':
		file.write(u'\t\t\t#' + comments + u'\n')
	
	return


def writedata(file, settings, data, dataold):
	"""
	function to write the data in the .th file
	
	INPUTS:
		file     : variable that sets the file.th
		settings : List of the settings of this survey section
		data     : data from this survey section
		dataold  : data from the previous survey section
	   
	OUTPUTS:
		None
		
	USAGE:
		writeheader_th(file, cavename, entrance)
		
	Author: Xavier Robert, Lima 2016/06/27
	Modif : Phil Vernant Feb 2022
	
	"""
	
	# dictl = length of the data line
	dictl = {u'Deca'  : 9,
	         u'Topof' : 10}

	# if Prof values used in .tro file, convert depth to depthchange to avoid interleaved lines in .th file
	dirs = settings[6].rstrip(u'\n\r').split(u',')
	if u'Prof' in settings :
		prof0 = 0.0                      # assuming that the first point is a 0, not sure if that is always the case.
		for i, elems in enumerate(data):
			prof = float(elems[4])
			if u'Dir' in dirs[1] :
				data[i][4] = str(np.round((-prof0 + prof),2))
			else :
				data[i][4] = str(np.round((+prof0 - prof),2))
			prof0 = prof
	if u'Deniv' in settings and u'Inv' in dirs[1] : 
		for i, elems in enumerate(data):
			data[i][4] = str(-float(elems[4]))
			
	i=0
	for elems in data:
		for k in [0,2]:
			if elems[k] == u'*':
				# remove the '*', and replace them with the right data !
				if i == 0: elems[k] = dataold[len(dataold)-1][k+1]
				else: elems[k] = data[i-1][k+1]
		for k in range (dictl[settings[0]]-4, dictl[settings[0]]):
			# Check that LRUD != '*'; If yes, change them to 0
#			if elems[k] == u'*': elems[k] = u'0'
			if elems[k] == u'*':
				if i == 0: elems[k] = dataold[len(dataold)-1][k]
				else: elems[k] = data[i-1][k]
		# remove duplicates of entrance station used by visualtopo for LRUD purpose
		# if not the same stations but distance = 0 replace 0 by 1mm, could be better coded 
		i+=1

	for i, elems in enumerate(data):
		if 	elems[0] == elems[1] :
			k = dictl[settings[0]]-4
			LRUD = elems[k:k+4]
			for j in np.arange(4) :
				data[i+1][k+j] = '['+LRUD[j]+' '+data[i+1][k+j]+']' 
			del data[i]
		if float(elems[2]) == 0.0 :
			data[i][2] = '0.001' 
						
	i=0
	for elems in data:
		# Check if option 'E'
		if u'E' in elems:
			file.write(u'\t\t\tflags duplicate \n')
		# We write the data
		file.write(u'\t\t\t' + u'\t'.join(x for x in elems[0:dictl[settings[0]]]))
		
		if len(elems) > (dictl[settings[0]] + 2):
			if elems[dictl[settings[0]] + 1] != u'N' and elems[dictl[settings[0]] + 1] != u'I':
				# we add the comment if there is one
				file.write(u'\t# ' + ' '.join(x for x in elems[(dictl[settings[0]]+1) : len(elems)])[1:-1] + u'\n')
			elif len(elems) > (dictl[settings[0]] + 3):
				file.write(u'\t# ' + ' '.join(x for x in elems[(dictl[settings[0]]+2) : len(elems)])[1:-1] + u'\n')
			else:
				file.write(u'\n')
		else:
			file.write(u'\n')
		if 	elems[(dictl[settings[0]])] == u'I':
			file.write(u'\t\t\textend reverse \n')
		if u'E' in elems:
			file.write(u'\t\t\tflags not duplicate \n')	
		i+=1
				
	return

# buildthconfig
def builddictcave(thconfigfnme= u'Test.thconfig'):
	"""
	
	"""
	
	########################
	#    Define parameters
	# thconfigfnme: name of the thconfig file
	#thconfigfnme= 'Test.thconfig'

	# sourcefiles: source files
	sourcefile = [u'example.th', u'example.th2', u'example-coupe.th2']
	# xviscale: scale of the xvi file
	#           1000 corresponds to 1/1000
	xviscale = 1000
	# xvigrid: spacing of the grid for the xvi, in meters
	xvigrid = 10
	# cavefnme: cave fnme
	cavefnme = u'Example'
	# coord: coordinate system
	#        Can be set to None
	coord = None
	# scale: scale of the map
	#        500 corresponds to 1/500
	scale = 500 
	
	
	datac = [thconfigfnme]
	dictcave = [sourcefile, xviscale, xvigrid, cavefnme, coord, scale]
	
	return dictcave, data


def writethconfig(pdata, dictcave):
	"""
		Function to write a .thconfig file for a cave
		
		INPUTS:
			pdata     : path and name of the .thconfig file
			dictcave  : list with [sourcefile, xviscale, xvigrid, cavefnme, coord, scale]
			
		OUTPUTS:
			thconfig file
			
		USAGE:
			writethconfig(dictcave):
			
	"""
	
	f2w = open(pdata, 'w')
	
	f2w.write(u'encoding utf-8 \n\n')
	f2w.write(u'# File written by pytro2th (Xavier Robert)  \n')
	f2w.write(u'# Copyright (C) 2021 Xavier Robert <xavier.robert@ird.fr> \n')
	f2w.write(u'# This work is under the licence Creatice Commonc CC-by-nc-sa v.4 \n\n')
  
  	
	# Do a loop on the input files
	#	To move in the cave-tot.th and only call that last file?
	for cfile in dictcave[0]:
		if (u'#' in cfile) : 
			f2w.write(u'#source ' + cfile[1:] + u'\n')
		else :
			f2w.write(u'source ' + cfile + u'\n')
	f2w.write(u'\n')
	  
  
	f2w.write(u'layout xviexport \n')
	f2w.write(u'\tscale 1 ' + str(dictcave[1]) + u' \n')
	f2w.write(u'\tgrid-size ' + str(dictcave[2]) + u' ' + str(dictcave[2]) + u' ' + str(dictcave[2]) + u' m \n')
	f2w.write(u'\tgrid bottom \n')
	f2w.write(u'endlayout \n')
	f2w.write(u'\n\n')
	
	# write a simple layout for the map and the profile
	f2w.write(u'layout base\n')
	f2w.write(u'\tdoc-title "' + str(dictcave[3]) + '"\n')
	f2w.write(u'\tcs ' + str(dictcave[4]) + ' \n')
	f2w.write(u'\tbase-scale 1 ' + str(dictcave[1]) + '\n')
	f2w.write(u'\tscale 1 ' + str(dictcave[5]) + u'\n')
	f2w.write(u'\t#color map-bg 100\n')
	f2w.write(u'\ttransparency on\n')
	f2w.write(u'\topacity 75\n')
	f2w.write(u'\tlegend on\n')
	f2w.write(u'\tmap-header 100 100 nw\n')
	f2w.write(u'\tsymbol-show line survey\n')
	f2w.write(u'\tsymbol-show point station\n')
	f2w.write(u'\tdebug station-names\n')
	f2w.write(u'\tgrid bottom\n')
	f2w.write(u'\tgrid-size 100 100 20 m\n')
	f2w.write(u'endlayout\n')

	
	f2w.write(u'\n\n')
	f2w.write(u'# 3-EXPORTS   \n')
	f2w.write(u'export map -fmt xvi -layout xviexport -o '+ dictcave[6] + u'-map.xvi\n')
	f2w.write(u'export map -projection extended -fmt xvi -layout xviexport -o '+ dictcave[6] + u'-coupe.xvi\n\n')
 
	f2w.write(u'export map -o '+ dictcave[6] + u'-plan.pdf -layout base\n')
	f2w.write(u'export map -projection extended -layout base -o '+ dictcave[6] + u'-coupe.pdf\n')
	f2w.write(u'export model -o '+ dictcave[6] + u'.lox\n\n')
 
	f2w.write(u'# Export des fichiers ESRI\n')
	f2w.write(u'export map -proj plan -fmt esri -o '+ dictcave[6] + u' -layout my_layout\n')
 
	f2w.write(u'# Export des fichiers kml\n')
	f2w.write(u'export model -fmt kml -o '+ dictcave[6] + u'.kml\n\n')

	
	f2w.closed
	
	print(u'\tFR : Fichier ' + pdata + u' créé')
	print(u'\tEN : File ' + pdata + u' written\n')
	
	return
	
def checkfiles(pdata):
	"""
	Function to check if the file exists
	Raise error if file exists

	INPUTS:
		pdata         : variable that sets the file to check
		Errorfiles    : boolean; if True (default), if pdata already exists, the program stops;
		                         if False, the programme erase the old pdata
	   
	OUTPUTS:
		None
		
	USAGE:
		checkfiles(pdata, Errorfiles = False)
		checkfiles(pdata)
		
	Author: Xavier Robert, Lima 2016/06/27
	"""
	# Check if file exists, if not, raise an error
	if os.path.isfile(pdata) == True :
			print(u'\tFR : ATTENTION: le fichier %s a été écrasé' % pdata)
			print(u'\tEN : WARNING  : file %s has be rewritten\n' % pdata)
	