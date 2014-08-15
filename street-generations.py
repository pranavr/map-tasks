import utils as utils
import math
import time
import datetime
import requests
import random
import hmac 
import base64
import hashlib
import urlparse	
import xml.etree.cElementTree as et
from bs4 import BeautifulSoup
import geojson
import json
from collections import OrderedDict



def decode(point_str):

    '''Decodes a polyline that has been encoded using Google's algorithm
    http://code.google.com/apis/maps/documentation/polylinealgorithm.html
    
    This is a generic method that returns a list of (latitude, longitude) 
    tuples.
    
    :param point_str: Encoded polyline string.
    :type point_str: string
    :returns: List of 2-tuples where each tuple is (latitude, longitude)
    :rtype: list
    
    Credit: https://gist.github.com/signed0/2031157
    '''
            
    # sone coordinate offset is represented by 4 to 5 binary chunks
    coord_chunks = [[]]
    for char in point_str:
        
        # convert each character to decimal from ascii
        value = ord(char) - 63
        
        # values that have a chunk following have an extra 1 on the left
        split_after = not (value & 0x20)         
        value &= 0x1F
        
        coord_chunks[-1].append(value)
        
        if split_after:
                coord_chunks.append([])
        
    del coord_chunks[-1]
    
    coords = []
    
    for coord_chunk in coord_chunks:
        coord = 0
        
        for i, chunk in enumerate(coord_chunk):                    
            coord |= chunk << (i * 5) 
        
        #there is a 1 on the right if the coord is negative
        if coord & 0x1:
            coord = ~coord #invert
        coord >>= 1
        coord /= 100000.0
                    
        coords.append(coord)
    
    # convert the 1 dimensional list to a 2 dimensional list and offsets to 
    # actual values
    points = []
    prev_x = 0
    prev_y = 0
    for i in xrange(0, len(coords) - 1, 2):
        if coords[i] == 0 and coords[i + 1] == 0:
            continue
        
        prev_x += coords[i + 1]
        prev_y += coords[i]
        # a round to 6 digits ensures that the floats are the same as when 
        # they were encoded
        points.append((round(prev_x, 6), round(prev_y, 6)))
    
    return points   


def pointsToSegments(points):
	segments= []
	index = 1
	while (index < len(points)):
		segment = [[points[index-1][1], points[index-1][0]], [points[index][1], points[index][0]]]
		segments.append(segment)
		index+=1
	return segments

def between(left,right,s):
    before,_,a = s.partition(left)
    a,_,after = a.partition(right)
    return a

def directionsService(origin, dest, mode, city):	
	departure_time=  str(int(time.mktime(time.gmtime())))
	url = 'http://maps.googleapis.com/maps/api/directions/xml?origin='+str(origin[0])+','+ str(origin[1])+'&destination='+str(dest[0])+','+ str(dest[1])+'&mode='+str(mode)+'&sensor=false'
	url2 = utils.createSecureURL(url)
	print url2
	xml = requests.get(url2)
	#print xml.status_code
	#print xml.content
	parse = et.XML(xml.content)

	if (parse.find('status').text == 'OK'):
		steps = parse.find('route').find('leg').findall('step')
		final_segments = []
		path = []
		generation = 0

		for step in steps:
			point_str = step.find('polyline').find('points').text
			points = decode(point_str)
			segments = pointsToSegments(points)
			instr = step.find('html_instructions').text
			instr = instr.split()
			containsName = ' '.join(instr[2:])
			name = between('<b>', '</b>',containsName)

			for segment in segments:
				[start_lat, start_lng] = segment[0]
				[end_lat, end_lng] = segment[1]
				#if isPathSegmentUnique(start_lat, start_lng, end_lat, end_lng, name):
				final_segments.append([start_lat, start_lng, end_lat, end_lng, name, generation])
			
			generation+=1

		path_str = parse.find('route').find('overview_polyline').find('points').text
		path = decode(path_str)

		
		return [final_segments, path]
	else:
		#savePathDict()
		print "RequestError: " + parse.find('status').text
		if parse.find('status').text =='ZERO_RESULTS':
			return [0,0]
		return [None, None]



def processData(city, station):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/generations/'
	segments = open(basePath+'generations_segments_backup.csv', 'r')
	segments = segments.readlines()
	d = OrderedDict()


	for segment in segments:
		segment = segment.split(',')
		if segment[4] != '':
			key = str(segment[0]) + ';' + str(segment[1]) + ';' + str(segment[2])+ ';' + str(segment[3]) + ';' + str(segment[4]) + ';' + str(segment[5])
			if key in d.keys():
				d[key] +=1
			else:
				d[key] = 1


	processedSegments = open(basePath+'generations_segments.csv', 'w')
	processedSegments.write('start_lat,start_lng,end_lat,end_lng,name,generation,station'+'\n')
	
	for seg in d.keys():
		[start_lat, start_lng, end_lat, end_lng, name, generation] = seg.split(';')
		processedSegments.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(generation)  + ',' + str(station) + '\n')
	
	print len(segments)
	print len(d.keys())



origins = {'Cambridge':{}}
origins['Cambridge']['harvard'] = [42.373368,-71.118647]



def controller(city, start):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/generations/'
	output = open(basePath+'generations_segments_backup.csv', 'a+')
	#output.write('start_lat,start_lng,end_lat,end_lng,name,generation,station,origin_lat,origin_lng'+ '\n')

	points = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/segment_points.csv', 'r')
	points = points.readlines()

	origin = origins[city][start]

	count = 5762
	while (count < len(points)):
		point = points[count]
		point = point.split(',')
		print point 
		latlng = [float(point[0]), float(point[1])]
		#closestStationCoords, closestStationName = findClosestStation(latlng, city)
		[segments,path] = directionsService(origin, latlng, 'walking',city)

		if segments != 0 and path != 0:
			if len(segments) >0:

				for [start_lat, start_lng, end_lat, end_lng, name, generation] in segments:
					if start_lat != None:
						key = str(start_lat) + ';' + str(start_lng) + ';' + str(end_lat)+ ';' + str(end_lng) + ';' + str(name)
						#opacity = pathDict[key] * 0.01
						name = name.replace(u'\u200e', '')
						output.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(generation) + ',' + str(start) + ',' +  str(latlng[0]) + ',' + str(latlng[1]) + '\n')
			

				# for [lat, lng] in path:
				# 	if lat != None:
				# 		output_paths.write(str(lat) + ',' + str(lng) + ',' + str(closestStationName) + ',' + str(latlng) + ' ; ')

				# output_paths.write('\n')

		

		print str(count) + " out of " + str(len(points)) 
		count+=1
		time.sleep(0.95)




processData('Cambridge', 'harvard')
#controller('Cambridge', 'harvard')
