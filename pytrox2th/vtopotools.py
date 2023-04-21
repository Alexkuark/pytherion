######!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf8

# Copyright (c) 2020 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


"""
	Functions to work on vtopo data to be able to write them in the Therion format
	By Xavier Robert
	Lima, 2016.06.21
	
	USAGE :
	  - They are normally used by other scripts
	
	
	INPUTS:
		The inputs are in the script file, in the "# Define data to analysis" section. 
		The different arguments are described.
		
"""

###### To DO :  #######
#    - Take in account the 'I' (extended elevation) inverse option in vtopo file --> set extend right/left
###### End To DO #######

from __future__ import  division
# This to be sure that the result of the division of integers is a real, not an integer
#from __future__ import unicode_literals

# Import modules
import sys, os
from datetime import datetime

############################################################################
def read_vtopo_header(cavite):
	"""
		Function to read header from vtopofile
		
		INPUTS:
			cavite: cave information from file .trox converted from xml to dictionary
		
		OUTPUTS (all are strings):
			cavename    : Name of the cave
			coordinates : Entrance coordinates
			coordsyst   : Coordinates system to set the entrance coordinates
			club        : Name of the group that explored the cave
			entrance    : Entrance of the cave
		
		USAGE:
			cavename, coordinates, coordsyst, club, entrance, versionfle = read_vtopo_header(lines)
				
		Author: Xavier Robert, Lima 2016/06/27
		modif : Phil Vernant 2022/02/08
		modif : Alex Guizard 2023/04/05
		
		Licence: CCby-nc
	"""
	
	# coord_dict: French Lambert system. To find number of your system, see extern/proj4/nad/epsg 
	#             file in the therion source distribution. You can add your own lines/systems
	coord_dict = {u'LT1' : u'EPSG:27571',
	             u'LT2' : u'EPSG:27572',
	             u'LT2E' : u'EPSG:27572',
	             u'LT3' : u'EPSG:27573',
	             u'LT4' : u'EPSG:27574',
	             u'LT72' : u'EPSG:31370',
	             u'LT9' : u'EPSG:2154',
	             u'LT93' : u'EPSG:2154',
	             u'SWISS' : u'EPSG:2056',
	             u'UTM30' : u'EPSG:32630',
	             u'UTM31' : u'EPSG:32631',
	             u'UTM32' : u'EPSG:32632',
	             u'UTM30E' : u'EPSG:23030',
	             u'UTM31E' : u'EPSG:23031',
	             u'UTM32E' : u'EPSG:23032'
	             }
	
	if u'Nom' in cavite.keys():
		cavename = cavite[u'Nom']
	else:
		cavename = ''
	if u'Coordonnees' in cavite.keys():
		coordinates = [cavite[u'Coordonnees'][u'@X'], cavite[u'Coordonnees'][u'@Y'], cavite[u'Coordonnees'][u'@Z']]
		if u'@Projection' in cavite[u'Coordonnees'].keys() and cavite[u'Coordonnees'][u'@Projection'] in coord_dict and (float(cavite[u'Coordonnees'][u'@X']) != 0.0 or float(cavite[u'Coordonnees'][u'@Y']) != 0.0):
			# Rewrite the coordinate system to be read by Therion
			# French Lambert system. To find number of your system, see extern/proj4/nad/epsg file in the therion source distribution. You can add you own lines/systems
			coordsyst = coord_dict[cavite[u'Coordonnees'][u'@Projection']]
		else:
			coordsyst = None
	else:
		coordinates = [0.0, 0.0, 0.0]
		coordsyst = None
	if u'Club' in cavite.keys():
		club = cavite[u'Club']
	else:
		club = None
	if u'Entree' in cavite.keys():
		entrance = cavite[u'Entree']
	else:
		entrance = None
	
	versionfle = None

	return cavename, coordinates, coordsyst, club, entrance


############################################################################	
def read_settings(param):
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
		Modif : Alex Guizard Mar 2022
		
		Licence: CCby-nc
	"""
	
	if u'Commentaire' in param.keys():
		comments = param[u'Commentaire']
	
	#date of survey
	if u'Date' in param.keys():
		try:
			param[u'Date'] = datetime.strptime(param[u'Date'], "%d/%m/%Y")
			
		except ValueError:
			print(param[u'Date'] + u' is not a valid date, date is not set for the survey')
			comments = param[u'Date'] + u' ' + comments
	
	return param, comments#.encode('utf-8', errors = "replace")


############################################################################
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


############################################################################
def convert_text(lines):
	"""
		Fonction to convert characters encoding...
		The problem is that .tro files are encode with strange Windows settings, 
		and the accentuation is not well understood by other systems
		
		Bug, that is not working well
		
		INPUTS:
			lines :
		OUTPUTS:
			
		
		USAGE:
			lines = convert_text(lines)
			
		Author: Xavier Robert, Lima 2016/06/27
		
		Licence: CCby-nc
	"""
	dictcaract ={'\xe8' : u'è',
	             '\xe0' : u'à',
	             '\xe9' : u'é',
	             '\xe0' : u'à',
	             '\xf9' : u'ù',
	             '\xea' : u'ê',
	             '\xeb' : u'ë',
	             '\xf1' : u'ñ',
	             '\xfb' : u'û',
	             '\xee' : u'î',
	             '\xef' : u'ï'}
	
	for line in lines:
	#for line in lines.decode('cp1252'):
		#line = line.decode('cp1252')
		# windows = latin-1 ? cp-1252 ? cp1252 ? mbcs ?
		for elem in dictcaract:
			#print line
			if elem in line:
				line = line.replace(elem, dictcaract[elem])
			
	return lines


############################################################################
if __name__ == u"__main__":
	"""
	Function to test sub-functions
	"""
	from datathwritetools import writeheader_th, writecenterlineheader, writedata
	
	fle_tro_fnme = u'Test.tro'
	fle_th_fnme = u'test.th'
	icomments = True
	thlang = u'fr'
	cavename = u'cave'
	
	# open tro file
	fle_tro = open(fle_tro_fnme, u'rU')
	# open new th file
	fle_th =  open(cavename.replace(u' ', u'_') + '/Data/' + fle_th_fnme, u'w')
	
	# read the tro file
	lines = fle_tro.readlines()
	lines = convert_text(lines)
	
	# read the header
	#cavename, coordinates, coordtro, club, entrance = read_vtopo_header(fle_tro)
	cavename, coordinates, coordsyst, club, entrance, versionfle = read_vtopo_header(lines)
	
	writeheader_th(fle_th, cavename, entrance)
	
	# read line to line and find the Param
	i = 0
	iline = []
	dataold = []
	
	# get line numbers of the lines beginning with 'Param'
	for line in lines:
		#print i
		#print i, line.replace('\n', '')
		if u'Param' in line: iline.append(i)
		i+=1
	
	for j in iline:
		# read the settings of the survey
		settings, comments = read_settings(lines[j].replace(u'\n', u''))
		data = read_data(lines, settings, j, iline)
		
		# write centerline header
		writecenterlineheader(fle_th, entrance, settings, comments, data, coordsyst, coordinates, club,
		                      icomments, thlang)
		# write the data to the .th file
		writedata(fle_th, settings, data, dataold)
		
		fle_th.write(u'\n\tendcenterline\n')
		dataold = data	
	
	
	fle_th.write(u'\nendsurvey\n')
	
	fle_tro.close
	fle_th.close

