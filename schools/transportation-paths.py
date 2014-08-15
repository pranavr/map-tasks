import requests
#import findImages as helper
import utils as utils
import math
import time
import datetime
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
import atexit




def createSecureURL(url):
	
	urlToSign = url.path + "?" + url.query

	privateKey = '7HyrvDsrV6trC91E-E7F6xpjWjs='
	decodedKey = base64.urlsafe_b64decode(privateKey)
	signature = hmac.new(decodedKey, urlToSign, hashlib.sha1)
	encodedSignature = base64.urlsafe_b64encode(signature.digest())
	originalUrl = url.scheme + '://' + url.netloc + url.path + "?" + url.query
	fullURL = originalUrl + "&signature=" + encodedSignature
	#print "URL = " + fullURL
	return fullURL


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



def isPathSegmentUnique(start_lat, start_lng, end_lat, end_lng,name):
	key = str(start_lat) + ';' + str(start_lng) + ';' + str(end_lat)+ ';' + str(end_lng) + ';' + str(name)
	if key in pathDict.keys():
		pathDict[key] +=1
		return False
	else:
		pathDict[key] = 1
		return True
	

def directionsService(origin, dest, mode, city):	
	departure_time=  str(int(time.mktime(time.gmtime())))
	url = urlparse.urlparse('http://maps.googleapis.com/maps/api/directions/xml?origin='+str(origin[0])+','+ str(origin[1])+'&destination='+str(dest[0])+','+ str(dest[1])+'&mode='+str(mode)+'&sensor=false&client=gme-mitisandt')
	url2 = createSecureURL(url)
	print url2
	xml = requests.get(url2)
	#print xml.status_code
	#print xml.content
	parse = et.XML(xml.content)

	if (parse.find('status').text == 'OK'):
		steps = parse.find('route').find('leg').findall('step')
		final_segments = []
		path = []
		for step in steps:
			# start_lat = float(step.find('start_location').find('lat').text)
			# start_lng = float(step.find('start_location').find('lng').text)
			# end_lat = float(step.find('end_location').find('lat').text)
			# end_lng = float(step.find('end_location').find('lng').text)

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
				final_segments.append([start_lat, start_lng, end_lat, end_lng, name])
			

		path_str = parse.find('route').find('overview_polyline').find('points').text
		path = decode(path_str)

		duration = float(parse.find('route').find('leg').find('duration').find('value').text)
		distance = float(parse.find('route').find('leg').find('distance').find('value').text)

		#savePathDict(city)
		
		return [final_segments, path, duration, distance]
	else:
		#savePathDict()
		status = parse.find('status').text
		print "RequestError: " + status
		if status =='ZERO_RESULTS' or status =='UNKNOWN_ERROR':
			return [0,0,0,0]
		return [None, None]




def savePathDict():
	dictFile = open('static/data/Cambridge/footfall/path_dict.json', 'w')
	json_data = json.dumps(pathDict)
	dictFile.write(json_data)

def between(left,right,s):
    before,_,a = s.partition(left)
    a,_,after = a.partition(right)
    return a


def findClosestStation(point, city):
	bestDist = 10000
	bestStation = ''
	stations= origins[city].keys()
	for i in range(len(stations)):
		dist = utils.compute_distance(point, origins[city][stations[i]])
		if dist < bestDist:
			bestDist = dist
			bestStation = stations[i]

	return origins[city][bestStation], bestStation




def printStations(city):
	output = open('static/data/'+str(city)+'/footfall/stations.csv', 'a+')
	output.write('lat,lng,name'+ '\n')
	for station in origins[city].keys():
		output.write(str(origins[city][station][0])+ ',' + str(origins[city][station][1]) + ',' + str(station) + '\n')




def loadPathDict(city):
	json_data = open('static/data/'+str(city)+'/footfall/path_dict.json').read()
	pathDict = json.loads(json_data)


pathDict = {}


def controllerBestStation(city, mode):
	basePathHome = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/footfall/'
	basePathSchools = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/schools/transportation/'

	output = open(basePathSchools+mode+'_segments_backup.csv', 'a+')
	output.write('start_lat,start_lng,end_lat,end_lng,name,station,origin_lat,origin_lng'+ '\n')
	output_paths = open(basePathSchools+mode+'_paths_complete.csv', 'w')
	points = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/segment_points.csv', 'r')
	points = points.readlines()


	count = 0
	while (count < len(points)):
		point = points[count]
		point = point.split(',')
		print point 
		latlng = [float(point[0]), float(point[1])]
		closestStationCoords, closestStationName = findClosestStation(latlng, city)
		print closestStationCoords, closestStationName
		[segments,path] = directionsService(closestStationCoords, latlng, mode,city)

		if segments != 0 and path != 0:
			if len(segments) >0:

				for [start_lat, start_lng, end_lat, end_lng, name] in segments:
					if start_lat != None:
						key = str(start_lat) + ';' + str(start_lng) + ';' + str(end_lat)+ ';' + str(end_lng) + ';' + str(name)
						#opacity = pathDict[key] * 0.01
						name = name.replace(u'\u200e', '')
						output.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(closestStationName) + ',' +  str(latlng[0]) + ',' + str(latlng[1]) + '\n')
			

				for [lat, lng] in path:
					if lat != None:
						output_paths.write(str(lat) + ',' + str(lng) + ',' + str(closestStationName) + ',' + str(latlng) + ' ; ')

				output_paths.write('\n')

		

		print str(count) + " out of " + str(len(points)) 
		count+=1
		time.sleep(0.5)


def controllerBestStation(city, mode):
	basePathHome = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/footfall/'
	basePathSchools = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/schools/transportation/'

	output = open(basePathSchools+mode+'_segments_backup.csv', 'a+')
	output.write('start_lat,start_lng,end_lat,end_lng,name,station,origin_lat,origin_lng'+ '\n')
	output_paths = open(basePathSchools+mode+'_paths_complete.csv', 'w')
	points = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/segment_points.csv', 'r')
	points = points.readlines()


	count = 0
	while (count < len(points)):
		point = points[count]
		point = point.split(',')
		print point 
		latlng = [float(point[0]), float(point[1])]
		closestStationCoords, closestStationName = findClosestStation(latlng, city)
		print closestStationCoords, closestStationName
		[segments,path] = directionsService(closestStationCoords, latlng, mode,city)

		if segments != 0 and path != 0:
			if len(segments) >0:

				for [start_lat, start_lng, end_lat, end_lng, name] in segments:
					if start_lat != None:
						key = str(start_lat) + ';' + str(start_lng) + ';' + str(end_lat)+ ';' + str(end_lng) + ';' + str(name)
						#opacity = pathDict[key] * 0.01
						name = name.replace(u'\u200e', '')
						output.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(closestStationName) + ',' +  str(latlng[0]) + ',' + str(latlng[1]) + '\n')
			

				for [lat, lng] in path:
					if lat != None:
						output_paths.write(str(lat) + ',' + str(lng) + ',' + str(closestStationName) + ',' + str(latlng) + ' ; ')

				output_paths.write('\n')

		

		print str(count) + " out of " + str(len(points)) 
		count+=1
		time.sleep(0.5)

def controllerAllStations(city, mode):



	basePathHome = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/footfall/'
	basePathSchools = '/Users/pranavramkrishnan/Desktop/Research/schools/transportation/'

	points = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/segment_points.csv', 'r')
	points = points.readlines()

	stations =open(basePathSchools+'../public_schools.csv', 'r')
	stations = stations.readlines()


	schoolIndex = 3
	count = 1758


	# while (iS < len(stations)):

	station = stations[schoolIndex]
	station  = station.split(',')
	[lat, lng] = [station[1], station[2]]
	origin = [float(lat), float(lng)]
	schoolName = station[0]

	output = open(basePathSchools+schoolName+ '_'+mode+'_segments_backup.csv', 'a+')
	output_dist_duration = open(basePathSchools+schoolName + '_'+ mode+'_duration_distance.csv', 'a+')
	# output.write('start_lat,start_lng,end_lat,end_lng,name,station,origin_lat,origin_lng'+ '\n')
	output_paths = open(basePathSchools+schoolName + '_'+ mode+'_paths_complete.csv', 'w')
	

	while (count < len(points)):
		point = points[count]
		point = point.split(',')
		print point 
		latlng = [float(point[0]), float(point[1])]
		#closestStationCoords, closestStationName = findClosestStation(latlng, city)
		#print closestStationCoords, closestStationName

		[segments,path, duration, distance] = directionsService(origin, latlng, mode,city)

		if segments != 0 and path != 0:
			if len(segments) >0:

				for [start_lat, start_lng, end_lat, end_lng, name] in segments:
					if start_lat != None:
						key = str(start_lat) + ';' + str(start_lng) + ';' + str(end_lat)+ ';' + str(end_lng) + ';' + str(name)
						#opacity = pathDict[key] * 0.01
						name = name.replace(u'\u200e', '')
						output.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(schoolName) + ',' +  str(latlng[0]) + ',' + str(latlng[1]) + '\n')
			

				# for [lat, lng] in path:
				# 	if lat != None:
				# 		output_paths.write(str(lat) + ',' + str(lng) + ',' + str(schoolName) + ',' + str(latlng) + ' ; ')

				# output_paths.write('\n')

				output_dist_duration.write(str(count)+','+ str(latlng[0]) + ',' + str(latlng[1]) + ',' + str(schoolName) +','+ str(duration) +',' + str(distance) + '\n')
		
		print '______________'
		print str(count) + " out of " + str(len(points))  + ' of ' + str(schoolIndex) + ' out of ' + str(len(stations)) + ' stations'
		count+=1
		time.sleep(0.5)





def processData(city):
	basePathHome = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+city+'/footfall/'
	basePathSchools = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/schools/transportation/'
	segments = open(basePath+'walking_segments_backup.csv', 'r')
	segments = segments.readlines()
	d = OrderedDict()
	stations = OrderedDict()
	for segment in segments:
		segment = segment.split(',')
		if segment[4] != '':
			key = str(segment[0]) + ';' + str(segment[1]) + ';' + str(segment[2])+ ';' + str(segment[3]) + ';' + str(segment[4])
			if key in d.keys():
				d[key] +=1
			else:
				d[key] = 1

			station = segment[5][:len(segment[5])]
			stations[key] = station

	maxValue = max(d.values())
	print maxValue
	processedSegments = open(basePath+'walking_segments.csv', 'w')
	processedSegments.write('start_lat,start_lng,end_lat,end_lng,name,station,opacity'+'\n')
	for seg in d.keys():
		value = d[seg]
		#opacity = math.pow(value/maxValue,1) +0.05
		opacity = value * 0.01
		station = stations[seg]
		print seg, station
		[start_lat, start_lng, end_lat, end_lng, name] = seg.split(';')
		processedSegments.write(str(start_lat) + ',' + str(start_lng) + ',' + str(end_lat) + ',' + str(end_lng) + ',' + str(name) + ',' + str(station) + ',' + str(opacity) + '\n')





	print len(segments)
	print len(d.keys())

def splitBySchool(city, mode):
	basePathSchools = '/Users/pranavramkrishnan/Desktop/Research/schools/transportation/'
	alldurationdistanceData = open(basePathSchools+'walking_segments_backup.csv', 'r')
	alldurationdistanceData = alldurationdistanceData.readlines()
	for dura_dist in alldurationdistanceData:
		line = dura_dist.split(',')
		schoolName = line[5]
		output_dist_duration = open(basePathSchools+schoolName + '_'+ mode+'_segments_backup.csv', 'a+')
		output_dist_duration.write(dura_dist)



def paths_geojson(city):

	paths = open('static/data/'+str(city)+'/footfall/walking_paths_complete.csv', 'r')
	paths = paths.readlines()
	json_paths  = []
	for path in paths:
		new_path = []
		points = path.split(';')[:-1]
		for point in points:
			[lng, lat] = point.split(',')
			new_path.append((float(lat), float(lng)))
		json_paths.append(new_path)

	geojson_paths = geojson.MultiLineString(json_paths)
	geojson_data = geojson.dumps(geojson_paths)
	output_file = open('static/data/'+str(city)+'/footfall/walking_paths.geojson','w')
	output_file.write(geojson_data)


# atexit.register(savePathDict)



#splitBySchool('Cambridge', 'walking')
controllerAllStations('Cambridge', 'walking')
#processData('Manhattan')
#paths_geojson('Cambridge')

