######!/usr/bin/env python
# -*- coding: utf8 -*-
# coding: utf8

# Copyright (c) 2020 Xavier Robert <xavier.robert@ird.fr>
# SPDX-License-Identifier: GPL-3.0-or-later


"""
	!---------------------------------------------------------!
	!                                                         !
	!                    Trox to Therion                       !
	!                                                         !
	!           Code to transform the .trox files              !
	!            Visual Topo into files that can              !
	!                  be used by Therion                     !
	!               					  !
	!		OSU OREME				  !
	!		by Philippe Vernant, Alexis Guizard	  !
	!              From pytherion by Xavier Robert            !
	!                                                         !
	!---------------------------------------------------------!

	 ENGLISH :
	 This code is to transform the .trox file from Visualtopo (http://vtopo.free.fr/)
	 into files that can be read by Therion (http://therion.speleo.sk/).
	 It reads .trox file and produce one .th file (file with survey data),
	 and one thconfig file (file that is used to compile and build the survey with Therion).
	 
	 TODOS : - Correct the errors in encodings... This is the most important....
	         - Check all the situations possibles...
	         - Add title to the centerline !
"""
# Do divisions with Reals, not with integers
# Must be at the beginning of the file
from __future__ import division
#from __future__ import unicode_literals
import sys, os, wget
from pyproj import Transformer
import xmltodict

# Import Python modules
#modulesNames = ['sys', 'warnings']
#for module in modulesNames:
#	try:
#		# because we want to import using a variable, do it this way
#		module_obj = __import__(module)
#		# create a global object containging our module
#		globals()[module] = module_obj
#	except ImportError:
#		sys.exit("ERROR : Module " + module + " not present. \n\n Please, install it \
#			      \n\n Edit the source code for more information")

#from .buildparam import *
from .vtopotools import *
from .datathwritetools import *
from .buildthconfig import *


def trox2th(fle_trox_fnme = None, fle_th_fnme = None, 
			thlang = u'fr',
			cavename = None, 
			icomments = True, icoupe = True, 
			ithconfig = True, istructure = True, thconfigfnme = None, 
			ithc = True, thcpath = None, thcfnme = u'config.thc', 
			sourcefile = None, xviscale = 1000, xvigrid = 10, scale = 500,
			Errorfiles = True):
	
	"""
		Main function to convert trox to th files. 
		This is this function that should be called from python.
	
		INPUTS:
			fle_trox_fnme : (string) Path and name of the .trox file to convert. 
			               if None (value by default), the function does not convert anything 
			               but build .thconfig and config.thc files
			               If the path is not given, the function will look in the folder from where it is launched
			fle_th_fnme  : (string) Path and name of the .th file to create from the .trox file. 
			               If None (value by default), this file is created from the .trox file name 
			               and in the same folder than that .trox file
			thlang       : (string) String that set the language. 'fr' by default. 
			               If you need english, change 'fr' to 'en' in the function definition
			              set 'fr' for french
			              set 'en' for english
			              ... other languages are not implemented
			cavename     : (string) Name of the cave. 
			               If set to None (default value), it is get from the .trox file.
			icomments    : (Boolean) To add (True, by default) or not (False) comments in the produced files
			icoupe       : (Boolean) To set (True, by default) or not (False) an extended-elevation layout in the .thconfig file
			ithconfig    : (Boolean) To set if the thconfig file is created (True, by default) or not 
			istructure   : (Boolean) To set if the structure and the addditional files are created (True, by default) or not 
			thconfigfnme : (string) Path and name of the thconfig file. 
			               If None (by default), path and name build from the .trox file
			ithc         : (Boolean) To build (True, by default) or not (False) a config file config.thc 
			thcpath      : (string) Path to the directry that contains the config file called in the cave.thconfig file.
			                If used with ithc = False, this path is only used for the declaration 
			                in the cave.thconfig
			                If used with ithc = True, the config file will be written in that directory.
			                Set to None by default
			thcfnme      : (string) Name of the config.thc (value by default if set to None or if ommitted)
			sourcefile   : (list of strings) Define the source files declared in the cave.thconfig
							ex :['example.th', 'example.th2', 'example-coupe.th2']
							If None or ommitted, it is build from the .trox file or the cavename
			xviscale     : (Real) Scale of the xvi file. 
			                Set to 1000 by default that corresponds to 1/1000 
			xvigrid      : (Real) Spacing of the grid for the xvi, in meters. 
			               Set 10 by default
			scale        : (Real) scale of the map
			               Set to 500 by default that corresponds to 1/500 	
			Errorfiles   : (Boolean) If True (by default), an error will be raised if output files exists in the folder
			               If False, only a warning is raised, and the previous files are erased by the new ones.
			               Use with caution
			
		OUTPUTS:
			Depending of the parameters inputed, several files can be produced
			cavename.th       : survey data for Therion
			cavename.thconfig : file to build the pdf's maps and others
			confgi.thc        : config file for the .thconfig file.
			
		USAGE:
			To build everything
			trox2th(fle_trox_fnme = 'Test', fle_th_fnme = 'Test', 
			       thlang = 'fr',
			       cavename = 'Test', 
			       icomments = True, icoupe = True, 
			       ithconfig = True, thconfigfnme = None, 
			       ithc = True, thcpath = None, thcfnme = 'config.thc', 
			       sourcefiles = None, xviscale = 1000, xvigrid = 10, scale = 500,
			       Errorfiles = True)
			
			To build only a .th file
			trox2th(fle_trox_fnme = 'Test', fle_th_fnme = 'Test', 
			       thlang = 'fr',
			       cavename = 'Test', 
			       icomments = True, icoupe = True, 
			       ithconfig = False
			       ithc = False
			       Errorfiles = True)
			
			To build only a thonfig file, in english, without any comments and without extended elevation layout
			trox2th(thlang = 'en',
			       cavename = 'Test', 
			       icomments = False, icoupe = False, 
			       ithconfig = False, thconfigfnme = None, 
			       ithc = False, thcpath = my/path/to/my/confg/file, thcfnme = 'config.thc', 
			       sourcefiles = ['Test.th', 'Test.th2'], xviscale = 1000, xvigrid = 10, scale = 500,
			       Errorfiles = True)
		
		Author: Xavier Robert, Lima 2016/06/27
		
		Licence: CCby-nc
	"""
	
	if thlang in [u'fr', u'FR', u'Fr', u'fR']: thlang = u'fr'
	elif thlang in [u'en',u'EN', u'En', u'eN']: thlang = u'en'
	else: raise NameError(u'ERROR: Language %s not implemented\n'
	                      u'       Use "en" instead' % thlang )
	print(u'____________________________________________________________\n\n\t\tTROX 2 THERION\n____________________________________________________________\n')
	if thlang == u'fr':
		print(u'\nPhilippe Vernant, Alexis Guizard, OSU OREME - Montpellier, France\nEcrit par Xavier Robert, Groupe spéléo Vulcain - Lyon, France\n')
	elif thlang == u'en':
		print(u'\nPhilippe Vernant, Alexis Guizard, OSU OREME - Montpellier, France\nWritten by Xavier Robert, Groupe spéléo Vulcain - Lyon, France\n')
	print(u'____________________________________________________________\n\n')
	
	coordsyst = None
	coordinates = None
	if fle_trox_fnme is not None:
		if fle_trox_fnme[-5:] != u'.trox':
			fle_trox_fnme = fle_trox_fnme + u'.trox'
		# check if file exists
		if os.path.isfile(fle_trox_fnme) == False :
			if thlang == u'fr': raise NameError(u'ERROR : Le fichier %s n\'existe pas' %(str(fle_tro_fnme)))
			elif thlang == u'en': raise NameError(u'ERROR : File %s does not exist' %(str(fle_tro_fnme)))
		
		if fle_th_fnme is None:
			# convert trox file to th file
			if thlang == u'fr': print(u'\tPas de nom fichier .th en entrée, le fichier sera nommé avec le nom de la cavité')
			elif thlang == u'en': print(u'\tNo .th File name input, the Therion file name will be the cave name')
			cavename, coordinates, coordsyst, fle_th_fnme = convert_trox(fle_trox_fnme, 
			                                              icomments = icomments, icoupe = icoupe, istructure = istructure, 
			                                              thlang = thlang, Errorfiles = Errorfiles)
		else:
			if thlang == u'fr': print(u'\tLe fichier Therion sera nommé comme indiqué en paramètre %s ' %(fle_th_fnme))
			elif thlang == u'en': print(u'\tTherion File will be name as set in parameter %s ' %(fle_th_fnme))
			cavename, coordinates, coordsyst, fle_th_fnme = convert_trox(fle_trox_fnme, fle_th_fnme, cavename,
			                                               icomments = icomments, icoupe = icoupe, istructure = istructure,
			                                               thlang = thlang, Errorfiles = Errorfiles)
		if thlang == u'fr': print(u'\tFichier Therion %s construit à partir des données %s' %(fle_th_fnme, fle_trox_fnme))
		elif thlang == u'en': print(u'\tFile %s built from %s' %(fle_th_fnme, fle_trox_fnme))
	else:
		if thlang == u'fr': print(u'\tPas de fichier .trox en entrée, pas de fichier de données .th créé...')
		elif thlang == u'en': print(u'\tNo .trox File input, no .th data file created...')
		# Build here the new structure:
		if istructure: build_structure(u'cave', Errorfiles = True)

	if sourcefile is None:
		if fle_th_fnme is None:

			sourcefile = [cavename.replace(u' ', u'_') + u'.th', 
			              u'#' + cavename.replace(u' ', u'_') + u'.th2', 
			              u'#' + cavename.replace(u' ', u'_') + u'-coupe.th2']
		else:
			sourcefile = [fle_th_fnme, u'#' + fle_th_fnme[0:-4] + u'th2', u'#' + fle_th_fnme[0:-4] + u'-coupe.th2' ]
	# Build the dictionnary for the thconfig file	
	dictcave = [sourcefile, xviscale, xvigrid, cavename, coordsyst, scale]

	# build thc file
	if ithc :
		if  thcpath is not None :
			# Download the config file from my github page
			try:
				wget.download('https://raw.githubusercontent.com/robertxa/Th-Config-Xav/master/config.thc', 
				               thcpath)
							   #thcpath + thcfnme)
			except HTTPError:
				if thcpath[-1] not in ['/', '\\']: thcpath = thcpath + '/'
				writethc(thcpath + thcfnme, istructure)
			except FileNotFoundError:
				if thcpath[-1] not in ['/', '\\']: thcpath = thcpath + '/'
				writethc(thcpath + thcfnme, istructure)
		else:
			# Download the config file from my github page
			try:
				if istructure: wget.download('https://raw.githubusercontent.com/robertxa/Th-Config-Xav/master/config.thc', 
				               cavename.replace(u' ', u'_') + '/')
				else: wget.download('https://raw.githubusercontent.com/robertxa/Th-Config-Xav/master/config.thc')
			except HTTPError:
				writethc(thcfnme, cavename, istructure)
			except FileNotFoundError:
				writethc(thcfnme, cavename, istructure)
	
	# build thconfig file
	if ithconfig :
		# write the file
		if thconfigfnme is None or thconfigfnme == u'' or thconfigfnme == u' ':
			if fle_th_fnme is None:	thconfigfnme = cavename.replace(u' ', u'_') + u'.thconfig'
			else: thconfigfnme = fle_th_fnme + u'config'
		
		#take in account istructure
		if istructure:
			thconfigfnme = cavename.replace(u' ', u'_') + '/' + thconfigfnme
		
		if thcpath is not None:
			thcfnme = thcpath + thcfnme
			writethconfig(thconfigfnme, icomments, icoupe, thlang,
			              dictcave,
		                  ithc, thcfnme)
		else:
			thcfnme = thcfnme
			writethconfig(thconfigfnme, icomments, icoupe, thlang,
			              dictcave,
		                  ithc, thcfnme)

	if istructure: 
		# build cavename-tot.th file
		f3w = open(cavename.replace(u' ', u'_') + '/' + cavename.replace(u' ', u'_') + '-tot.th', 'w')
		write_thtot(f3w, cavename,  icomments, thlang)
		f3w.closed
		print(u'\tFile ' + cavename.replace(u' ', u'_') + u'/' + cavename.replace(u' ', u'_') + u'-tot.th written...\n')	

		# build cavename-maps.th file
		f4w = open(cavename.replace(u' ', u'_') + u'/' + cavename.replace(u' ', u'_') + '-maps.th', 'w')
		write_thmaps(f4w, cavename, icomments, thlang)
		f4w.closed
		print(u'\tFile ' + cavename.replace(u' ', u'_') + u'/' + cavename.replace(u' ', u'_') + u'-maps.th written...\n\n')

		# build Legends/entrances-coordinates.th file
		f5w = open(cavename.replace(u' ', u'_') + '/Legends/entrances_coordinates.th', 'w')
		write_thcoords(f5w, cavename, coordinates, coordsyst, icomments, thlang)
		f5w.closed
		print(u'\tFile ' + cavename.replace(u' ', u'_') + u'/Legends/entrances_coordinates.th written...\n\n')

	print(u'____________________________________________________________')
	print(u'')
	
	return cavename, fle_th_fnme, thconfigfnme


def build_structure(cavename, Errorfiles = True):
	"""
	Check and build if needed the new structure:	
		-Cave/
			-Data/
				-cavename.th
				(-cavename.th2)
			-Legends/
				-entrances_coordinates.th
			-Outputs/
				-outputs.txt
			-Cavename.thconfig
			-cavename-tot.th
			-cavename-maps.th
			-config.thc
	
	INPUTS:
		cavename = name of the cave that is used to build all the folders and file structure
		Errorfiles = Boolean; If True (Default), the program stops if the structure already exists
							  If False or none, if the structure exists, it is erased

	OUTPUTS:
		None, except a new structure

	USAGE:
		build_structure(cavename, Errorfiles)

	"""
	
	# check if the folder cavename/ exists
	if os.path.exists(cavename.replace(u' ', u'_')):
		if Errorfiles:
			# Stop
			raise NameError(u'ERROR : Folder %s does exist' %(str(cavename.replace(u' ', u'_'))))
		else:
			print(u'WARNING: I have erased folder %s' % cavename.replace(u' ', u'_')) 
			if not os.path.exists(cavename.replace(u' ', u'_') + u'/Data'): os.mkdir(cavename.replace(u' ', u'_') + u'/Data')
			if not os.path.exists(cavename.replace(u' ', u'_') + u'/Legends'): os.mkdir(cavename.replace(u' ', u'_') + u'/Legends')
			if not os.path.exists(cavename.replace(u' ', u'_') + u'/Outputs'): 
				os.mkdir(cavename.replace(u' ', u'_') + u'/Outputs')
				# Add outputs.txt file
				mkfle_output_txt(cavename.replace(u' ', u'_'))
	#	- if no, create it and create the other files
	else:
		# Create the subfolders
		os.mkdir(cavename.replace(u' ', u'_'))
		os.mkdir(cavename.replace(u' ', u'_') + u'/Data')
		os.mkdir(cavename.replace(u' ', u'_') + u'/Outputs')
		# Add outputs.txt file
		mkfle_output_txt(cavename.replace(u' ', u'_'))
		os.mkdir(cavename.replace(u' ', u'_') + u'/Legends')
		
	return



def mkfle_output_txt(cavename):
	"""
	Build the file Output.txt in the folder cavename/Outputs/

	INPUTS:
		cavename = name of the cave

	OUTPUTS:
		None

	USAGE:
		create_output_txt(cavename)
	"""
	# Open the cavename/Outputs/outputs.txt file
	f1w = open(cavename.replace(u' ', u'_') + u'/Outputs/outputs.txt','w')
	f1w.write(u'Folder where Therion outputs are exported \n\n')
	# close the cavename/Outputs/outputs.txt file
	f1w.closed
	print(u'\tFile ' + cavename.replace(u' ', u'_') + u'/Outputs/outputs.txt written...')
	
	return



def convert_trox(fle_trox_fnme, fle_th_fnme = None, cavename = None, 
                icomments = True, icoupe = True, istructure = True, thlang = u'fr', Errorfiles = True):	
	"""
		Function that manages the trox 2 th conversion
		
		INPUTS:
			fle_trox_fnme : path and file name of the .trox file to convert
			fle_th_fnme  : path and file name of the .th file to create. 
			               If ommitted, set to None, and this varaible will be set in function of the fle_trox_fnme or cavename
			cavename     : Name of the cave. If ommitted, it is set to None, and it is get from the .trox file 
        	icomments    : (Boolean) To add (True, by default) or not (False) comments in the produced files
			icoupe       : (Boolean) To set (True, by default) or not (False) an extended-elevation layout in the .thconfig file
			istructure   : (Boolean) To set if the structure and the addditional files are created (True, by default) or not 
			thlang       : (string) String that set the language. 'fr' by default. 
			               If you need english, change 'fr' to 'en' in the function definition
			              set 'fr' for french
			              set 'en' for english
			
			Errorfiles   : True (by default if ommitted) to get an error if the .th file already exists.
	                       False if only a warning...
		OUTPUTS:
			new .th file with surveyed data for Therion
			cavename      : Name of the cave from the .trox file
			coordinates   : Coordinates of the entrance
			coordsyst     : Coordinates system used by the .trox file
			
		USAGE:
			cavename, coordsyst = convert_trox(fle_trox_fnme, [fle_th_fnme = fle_th_fnme, cavename = cavename, Errorfiles = Errorfiles])
			          fle_th_fnme, cavename and Errorfiles can be ommitted.
		
		Author: Xavier Robert, Lima 2016/06/27
		Modif : Phil Vernant, 2022/02/16
		Modif : Alex Guizard, 2023/04/05
		
		Licence: CCby-nc
	"""
	
	#from codecs import open
		
	# Initialization of some variables...
	#xcoord=0.
	#ycoord=0.
	#alt=0.
	
	# open the .trox survey	
	if thlang == u'fr': print(u'\tTravail sur %s' % fle_trox_fnme)
	elif thlang == u'en':print(u'\tProcessing %s' % fle_trox_fnme)
	print(' ')
	fle_trox = open(fle_trox_fnme, mode='rU', encoding='UTF-8')
	
	# read the .trox file
	trox = xmltodict.parse(fle_trox.read())
	# change the encoding 
	#lines = convert_text(lines)#not useful since encoding is set when opening file

	versionfle = trox[u'VisualTopo'][u'Version']
	# read the header
	coordinates = None
	cavename, coordinates, coordsyst, club, entrance = read_vtopo_header(trox[u'VisualTopo'][u'Cavite'])
	
	if cavename is None or cavename == '' or cavename == ' ' or cavename == '*' or cavename == '0.000':
		cavename = os.path.basename(fle_trox_fnme).replace(u'.trox', u'')
	
	if fle_th_fnme is None:
		fle_th_fnme = cavename.replace(u' ', u'_') + u'.th'
		print (fle_th_fnme)
	if fle_th_fnme[-3:] != u'.th':
		fle_th_fnme = fle_th_fnme + u'.th'	
	
	
	# Build here the new structure:
	if istructure: build_structure(cavename, Errorfiles)

	# check if file exists... 
	checkfiles(fle_th_fnme, Errorfiles)
	
	# open the .th file
	if istructure: fle_th = open (cavename.replace(u' ', u'_') + '/Data/' + fle_th_fnme, 'w')
	else: fle_th = open (fle_th_fnme, 'w')
	# write the .th header
	writeheader_th(fle_th, cavename, entrance)
	
	# initiate variables
	stations = {}
	
	#in case there is only one Param object
	if type(trox[u'VisualTopo'][u'Mesures'][u'Param']) is dict :
		trox[u'VisualTopo'][u'Mesures'][u'Param'] = [trox[u'VisualTopo'][u'Mesures'][u'Param']]
	
	for param in trox[u'VisualTopo'][u'Mesures'][u'Param']:
		# read the settings of the survey
		param = read_settings(param)
		
		# read the data from the trox file, get the end of surveys in .tro, not useful on .trox
		#data = read_data(lines, settings, j, iline)
		
		param, stations = convertdata(param, stations, entrance)
		
		if len(param[u'Visee']) > 0:
			# write centerline header
			writecenterlineheader(fle_th, entrance, param, coordsyst, coordinates, club,
					      icomments, thlang)

			# write the data to the .th file
			writedata(fle_th, param)

			# write the end of the centerline in the .th file
			fle_th.write(u'\n\tendcenterline\n\n')
	
	# write the end of the survey in the .th file
	fle_th.write(u'\nendsurvey\n')
	fle_th.close
	
	#print (fle_th_fnme)
	
	if thlang == u'fr': print (u'\tFichier %s écrit !' % fle_th_fnme)
	elif thlang == u'en': print (u'\tFile %s written!' % fle_th_fnme)
	
	return cavename, coordinates, coordsyst, fle_th_fnme


if __name__ == u'__main__':
	
	
	# initiate variables
	
	# run the transformation  
	trox2th()
