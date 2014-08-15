import geojson
import json
import utils as utils
import random
import time
import urllib2
import requests
import xml.etree.cElementTree as et
import shapely
from shapely.geometry import shape, Polygon, Point

def jsonToGeoJSON():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/transportation/'
	jsonVals = open(basePath + 'buildings_central_final.json', 'r')
	jsonVals = jsonVals.readlines()[0].split('},')
	features = []

	central = [42.365504,-71.103819]
	for line in jsonVals:
		
		lineElements = line.split(':')
		center = lineElements[1].split('],')[0].split(',')
		centerLat = float(center[0][2:])
		centerLng = float(center[1])
		center = [centerLng, centerLat]
		# color = str(lineElements[2].split(',')[0])
		# color = color[2:len(color)-1]

		coordinates = processPolygonCoordinate(lineElements[3].split(']],')[0] + ']]')
		bestMode = lineElements[4].split(',')[0]
		bestMode = bestMode[2:len(bestMode)-1]

		color = colorMapping(bestMode)

		datavals = lineElements[5].split('],')[0].split(',')
		datavals = [float(datavals[0][2:]), float(datavals[1]),float(datavals[2]),float(datavals[3]),float(datavals[4]),float(datavals[5]),float(datavals[6])]

		dist = utils.compute_distance([centerLat, centerLng], central)



		data_id_str = lineElements[len(lineElements)-1]
		if data_id_str[-2] == '}':
			data_id = int(data_id_str[:-2])
		else:
			data_id = int(data_id_str)

		relative_order = orderMapping(bestMode)
		polygon = geojson.Polygon(coordinates)
		properties = {"color": color,"bestMode":bestMode, "center":center, "distance": dist, "relative_order":relative_order}
		feature = geojson.Feature(geometry=polygon, properties=properties, id=data_id)
		features.append(feature)
	

	sorted_features = sorted(features, key = lambda k: (k.properties["relative_order"],k.properties["distance"]))
	featureColleciton = geojson.FeatureCollection(sorted_features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'central.geojson','w')
	output_file.write(geojson_data)



def orderMapping(mode):
	omap = {}
	omap['walking'] = 1
	omap['biking'] = 3
	omap['transit'] = 2
	omap['driving'] = 4
	return omap[mode]

def colorMapping(mode):

	cmap = {}
	cmap['walking'] = "#4dac26"
	cmap['transit'] = "#2b83ba"
	cmap['biking'] = "#fdae61"
	cmap['driving'] = "#d7191c"
	return cmap[mode]



def processPolygonCoordinate(coordinatesString):
	coordList = []
	coordinatesString = coordinatesString.split('],')
	for crd in coordinatesString:
		crd = crd.split(',')
		if crd[0][2] == '[':
			crdLat = float(crd[0][3:])
		else:
			crdLat = float(crd[0][2:])


		if crd[1][len(crd[1])-1] == ']':
			crdLng = float(crd[1][:len(crd[1])-2])
		else:
			crdLng = float(crd[1])

		coordList.append([crdLng, crdLat])
	return [coordList]


def directionsService(origin, dest, mode):	
	departure_time=  str(int(time.mktime(time.gmtime())))
	#url = 'http://maps.googleapis.com/maps/api/directions/xml?origin='+str(origin[0])+','+ str(origin[1])+'&destination='+str(dest[0])+','+ str(dest[1])+'&mode='+str(mode)+'&departure_time=' + str(departure_time) + '&sensor=false'
	url = 'http://maps.googleapis.com/maps/api/directions/xml?origin='+str(origin[0])+','+ str(origin[1])+'&destination='+str(dest[0])+','+ str(dest[1])+'&mode='+str(mode)+'&sensor=false'
	url2 = utils.createSecureURL(url)
	print url2
	xml = requests.get(url2)

	parse = et.XML(xml.content)

	if (parse.find('status').text == 'OK'):
		duration = float(parse.find('route').find('leg').find('duration').find('value').text)
		distance = float(parse.find('route').find('leg').find('distance').find('value').text)
		return [duration, distance]
	else:
		return [None, None]


def controller(city, mode,i=1,j=1):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/transportation/'
	jsonVals = open(basePath + 'block_groups_processed.geojson','r')
	geojsonData = geojson.load(jsonVals)
	idToCenters = {}

	for feat in geojsonData['features']:
		[lng, lat] = feat['properties']['center']
		shape_id = feat['id']
		idToCenters[shape_id] = (lat, lng)

	print shape_id,max(idToCenters.keys()), len(idToCenters.keys())

	output_file = open(basePath + mode+ '_values.csv', 'a+')

	while (i < len(idToCenters.keys())):
		(lat1, lng1) = idToCenters[i]
		while (j < len(idToCenters.keys())):
			(lat2, lng2) = idToCenters[j]
			[duration, distance] = directionsService([lat1, lng1], [lat2, lng2], mode)
			if duration != None and distance != None:
				output_file.write(str(i) + ',' + str(j) + ',' + str(duration) + ',' + str(distance) + '\n')	
				print "done with "+ str(i) + " , " + str(j) + " mode = " + str(mode)
				time.sleep(0.4)
			else:
				#output_file.write(str(i) + ',' + str(j) + ',' + str(0) + ',' + str(0) + '\n')	
				print "error ------ done with "+ str(i) + " , " + str(j) + " mode = " + str(mode)
			j+=1

		j = 1
		i +=1

def spotQuery(city, mode,i,j):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/transportation/'
	jsonVals = open(basePath + 'block_groups_processed.geojson','r')
	geojsonData = geojson.load(jsonVals)
	idToCenters = {}

	for feat in geojsonData['features']:
		[lng, lat] = feat['properties']['center']
		shape_id = feat['id']
		idToCenters[shape_id] = (lat, lng)

	output_file = open(basePath + mode+ '_values_check.csv', 'a+')

	(lat1, lng1) = idToCenters[i]
	(lat2, lng2) = idToCenters[j]
	[duration, distance] = directionsService([lat1, lng1], [lat2, lng2], mode)
	
	if duration != None and distance != None:
		output_file.write(str(i) + ',' + str(j) + ',' + str(duration) + ',' + str(distance) + '\n')	
		print "done with "+ str(i) + " , " + str(j) + " mode = " + str(mode)
		time.sleep(0.2)

def blockQuery(city, mode,id1,	id2 = 1):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/transportation/'
	jsonVals = open(basePath + 'block_groups_processed.geojson','r')
	geojsonData = geojson.load(jsonVals)
	idToCenters = {}

	for feat in geojsonData['features']:
		[lng, lat] = feat['properties']['center']
		shape_id = feat['id']
		idToCenters[shape_id] = (lat, lng)

	output_file = open(basePath + mode+ '_values_check.csv', 'a+')

	(lat1, lng1) = idToCenters[id1]
	while id2 in idToCenters:
		(lat2, lng2) = idToCenters[id2]
		[duration, distance] = directionsService([lat1, lng1], [lat2, lng2], mode)
	
		if duration != None and distance != None:
			output_file.write(str(id1) + ',' + str(lat1) + ',' + str(lng1) + ',' + str(id2)  + ',' + str(lat2) + ',' + str(lng2) + ',' + str(duration) + ',' + str(distance) + '\n')	
			print "done with "+ str(id1) + " , " + str(lat1) + ',' + str(lng1) + ',' + str(id2)  + ',' + str(lat2) + ',' + str(lng2) + ',' + " mode = " + str(mode)
		else:
			output_file.write(str(id1) + ',' + str(lat1) + ',' + str(lng1) + ',' + str(id2)  + ',' + str(lat2) + ',' + str(lng2) + ',' + str(1000) + ',' + str(1000) + '\n')	
		id2+=1
		time.sleep(0.6)


def findCentroid(coordinates):
	latMean = []
	lngMean = []


	if len(coordinates) ==1:
		processCoords = coordinates[0]
	else:
		processCoords = coordinates[1][0]

	# for crd in processCoords:
	# 	lngMean.append(float(crd[0]))
	# 	latMean.append(float(crd[1]))

	# lat = sum(latMean)/len(latMean)
	# lng = sum(lngMean)/len(lngMean)

	shapelyCoords =[]
	for crds in processCoords:
		shapelyCoords.append((crds[0], crds[1]))
	polygon = Polygon(shapelyCoords)
	centroid =  polygon.centroid
	return [centroid.x, centroid.y]

def loadGeoJSON(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+ str(city) + '/transportation/'
	jsonVals = open(basePath + 'processed1.geojson','r')
	geojsonData = geojson.load(jsonVals)
	features = []
	#i_d = 1
	largest = 1
	for feat in geojsonData['features']:
		geometry = feat['geometry']
		coordinates = geometry['coordinates']
		#polygon = shape(geometry)
		#area = polygon.area * 1000000
		# centerLat = float(feat['properties']['INTPTLAT10'])
		# centerLng = float(feat['properties']['INTPTLON10'])
		#center = [centerLng, centerLat]
		[centerLng, centerLat] = feat['properties']['center']
		#area = feat['properties']["Shape_Area"]
		#name = feat['properties']['NTAName']
		#bid = feat['properties']['CT2010']
		i_d = feat['id']
		#center = polygon.centroid
		shape_id = int(i_d)
		area = float(feat['properties']['area'])
		properties = {"center":[centerLng, centerLat], "area":area}
		feature = geojson.Feature(geometry=geometry, properties=properties, id=i_d)
		features.append(feature)
		#i_d+=1
	print id
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'block_groups_processed.geojson','w')
	output_file.write(geojson_data)



	# #modes = ['bicycling', 'driving']
	# modes = ['transit']


	# for mode in modes:
	# 	values = open(basePath + mode+ '_values.csv', 'r')
	# 	values = values.readlines()
	# 	for val in values:
	# 		val = val.split(',')
	# 		#print val
	# 		id1 = int(val[0])
	# 		id2 = int(val[1])
	# 		if val[2] != 'None' and val[3] != 'None':
	# 			duration = float(val[2])
	# 			distance = float(val[3])
	# 		else:
	# 			duration = 0
	# 			distance = 0

	# 		if mode =='driving':
	# 			duration += PARKING_TIME

	# 		# if id1 in valuesToJSON:
	# 		# 	if id2 in valuesToJSON[id1]:
	# 		# 		valuesToJSON[id1][id2]['duration'].append(duration)
	# 		# 	else:
	# 		# 		valuesToJSON[id1][id2] = {'duration':[duration]}
	# 		# else:
	# 		# 	valuesToJSON[id1] = {}
	# 		# 	valuesToJSON[id1][id2] = {'duration':[duration]}

	# 		if id1 > 279:
	# 			tempID = id2
	# 			id2 = id1
	# 			id1 = tempID


	# 		if id1 > id2: continue

	# 		if id1 in valuesToJSON:
	# 			if id2 in valuesToJSON[id1]:
	# 				valuesToJSON[id1][id2]['duration'].append(duration)
	# 				valuesToJSON[id1][id2]['labels'].append(mode)
	# 			else:
	# 				valuesToJSON[id1][id2] = {'duration':[duration], 'labels':[mode]}
	# 		else:
	# 			valuesToJSON[id1] = {}
	# 			valuesToJSON[id1][id2] = {'duration':[duration], 'labels':[mode]}

	# 		if id2 in valuesToJSON:
	# 			if id1 in valuesToJSON[id2]:
	# 				valuesToJSON[id2][id1]['duration'].append(duration)
	# 				valuesToJSON[id2][id1]['labels'].append(mode)
	# 			else:
	# 				valuesToJSON[id2][id1] = {'duration':[duration], 'labels':[mode]}
	# 		else:
	# 			valuesToJSON[id2] = {}
	# 			valuesToJSON[id2][id1] = {'duration':[duration], 'labels':[mode]}
			

	# #rangeScales= {'driving':[], 'bicycling':[], 'walking':[],'transit':[]}
	# rangeScales = {'transit':[]}


def csvToJSON(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) +'/transportation/'
	valuesToJSON = {}
	PARKING_TIME = 600	


	modes = ['bicycling','driving','transit']

	for mode in modes:
		values = open(basePath + mode+ '_values.csv', 'r')
		values = values.readlines()
		for val in values:
			val = val.split(',')
			#print mode,val
			#if mode == 'transit':

			# id1 = int(val[0])
			# id2 = int(val[1])
			# if val[2] != 'None' and val[3] != 'None':
			# 	duration = float(val[2])
			# 	distance = float(val[3])
			# else:
			# 	duration = None
			# 	distance = None
			# else:

			id1 = int(val[0])
			id2 = int(val[3])
			if val[2] != 'None' and val[3] != 'None':
				duration = float(val[6])
				distance = float(val[7])
			else:
				duration = None
				distance = None

			if mode =='driving':
	 			duration += PARKING_TIME

	 		# if mode=='bicycling' and (id1==398 or id2==398):
	 		# 	duration+=1000000

			if id1 in valuesToJSON:
				if id2 in valuesToJSON[id1]:
					valuesToJSON[id1][id2]['modes'][mode] = duration
				else:
					valuesToJSON[id1][id2] = {'modes':{mode:duration}}
			else:
				valuesToJSON[id1] ={id2: {'modes':{mode:duration}}}


			if id2 in valuesToJSON:
				if id1 in valuesToJSON[id2]:
					valuesToJSON[id2][id1]['modes'][mode] = duration
				else:
					valuesToJSON[id2][id1] = {'modes':{mode:duration}}
			else:
				valuesToJSON[id2] = {id1:{'modes':{mode:duration}}}



	rangeScales= {'driving':[], 'bicycling':[], 'walking':[],'transit':[]}
	#rangeScales = {'bicycling':[], 'walking':[]}

	#errors = open(basePath + 'errors.csv', 'a+')
	for id1 in valuesToJSON:
		for id2 in valuesToJSON[id1]:
			bestVal = 10000000
			bestMode = ''
			modes = valuesToJSON[id1][id2]['modes']

			

			values = valuesToJSON[id1][id2]
			for mode in values['modes'].keys():
				val = values['modes'][mode]
				if val < bestVal:
					bestVal = val
					bestMode = mode



			valuesToJSON[id1][id2]['bestMode'] = bestMode
			valuesToJSON[id1][id2]['bestVal'] = bestVal
			rangeScales[bestMode].append(bestVal)

			if id1==id2:
				valuesToJSON[id1][id2]['modes']['walking']=0.0
				valuesToJSON[id1][id2]['bestMode'] = 'walking'
				valuesToJSON[id1][id2]['bestVal'] = 100
				valuesToJSON[id2][id1]['modes']['walking']=0.0
				valuesToJSON[id2][id1]['bestMode'] = 'walking'
				valuesToJSON[id2][id1]['bestVal'] = 100
				rangeScales['walking'].append(100)
			
		
	idToArea = {}

	jsonVals = open(basePath + 'block_groups_processed.geojson','r')
	geojsonData = geojson.load(jsonVals)
	totalArea = 0

	for feat in geojsonData['features']:
		shape_id = feat['id']
		area = feat['properties']['area']
		idToArea[shape_id] = area
		totalArea += area
		#print shape_id, area

	finalJSON = {}

	
	for id1 in valuesToJSON:
		for id2 in valuesToJSON[id1]:
			print id1,id2
			bestMode = valuesToJSON[id1][id2]['bestMode']	
			bestVal = valuesToJSON[id1][id2]['bestVal'] 
			if id1 in finalJSON:
				if id2 in finalJSON[id1]:
					finalJSON[id1][id2]['bestMode'] = bestMode
					finalJSON[id1][id2]['bestVal'] = bestVal
				else:
					finalJSON[id1][id2] = {'bestMode':bestMode, 'bestVal':bestVal}
			else:
				finalJSON[id1]= {id2: {'bestMode':bestMode, 'bestVal':bestVal}}

	for id1 in valuesToJSON:
		areasDict = {'driving':0, 'bicycling':0, 'walking':0, 'transit':0}
		for id2 in valuesToJSON[id1]:
			bestMode = valuesToJSON[id1][id2]['bestMode']				
			areasDict[bestMode] += idToArea[id2]

		finalJSON[id1]['areas'] = {'driving': (areasDict['driving']/totalArea) * 100, 'walking':(areasDict['walking']/totalArea) * 100, 'bicycling':(areasDict['bicycling']/totalArea) * 100, 'transit':(areasDict['transit']/totalArea) * 100}



	finalJSON['ranges'] = {'driving':[], 'bicycling':[], 'walking':[],'transit':[]}
	#valuesToJSON['ranges'] = {'transit':[]}

	for mde in rangeScales:
		maxVal = max(rangeScales[mde])
		minVal = min(rangeScales[mde])
		finalJSON['ranges'][mde] = [minVal,maxVal]

	jsonValues = json.dumps(finalJSON)
	output_file = open(basePath + 'bestMode_values8.json','w')
	output_file.write(jsonValues)




def segmentDistance():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/'
	segments = open(basePath + 'final_segments_no_dup.csv', 'r').readlines()
	output_file = open(basePath + '/transportation/segment_walking_distances.csv','a+')
	i = 11
	while (i < len(segments)):
		seg = segments[i]
		seg = seg.split(',')
		[lat1, lng1, lat2,lng2] = [float(seg[1]), float(seg[2]), float(seg[3]), float(seg[4])]
		[duration,distance] = directionsService([lat1,lng1],[lat2, lng2], 'walking')
		output_file.write(seg[0] + ',' + str(lat1) + ',' + str(lng1)+ ','+ str(lat2) + ',' + str(lng2) + ','+str(duration)+',' +str(distance)+'\n')
		print "done i = " + str(i) + " out of " + str(len(segments))
		time.sleep(0.3)
		i+=1

def processNHoodnames():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/transportation/'
	jsonVals = open(basePath + 'neighborhoods.geojson','r')
	geojsonData = geojson.load(jsonVals)
	output_file = open(basePath + '/neighborhoods.csv','a+')
	for feat in geojsonData['features']:
		lat = feat['properties']['center_lat']
		lng = feat['properties']['center_lng']
		name = feat['properties']['NAME']
		output_file.write(str(lat) + ',' + str(lng) + ',' + str(name) + '\n')


def processNHoodnamesSANTAMONICA():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/SantaMonica/transportation/'
	jsonVals = open(basePath + 'neighborhoods.geojson','r')
	geojsonData = geojson.load(jsonVals)
	output_file = open(basePath + '/neighborhoods.csv','a+')
	for feat in geojsonData['features']:
		
		lat = feat['properties']['center_lat']
		lng = feat['properties']['center_lng']
		name = feat['properties']['NAME']
		output_file.write(str(lat) + ',' + str(lng) + ',' + str(name) + '\n')



def parseDistanceMatrix(xmlContent,ids,mode,city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/transportation/'
	output_file = open(basePath + mode+ '_values.csv', 'a+')

	parse = et.XML(xmlContent)

	rows = parse.findall('row')
	print rows, len(rows)
	for i in range(len(rows)):
		elements = rows[i].findall('element')
		id1= ids[i]
		for j in range(len(elements)):
			id2 = ids[j]
			elem_status = elements[j].find('status').text
			if elem_status == "OK":
				duration = elements[j].find('duration').find('value').text
				distance = elements[j].find('distance').find('value').text

				print duration
				output_file.write(str(id1) + ',' + str(id2) + ',' + str(duration) + ',' + str(distance) + '\n')	




def makeDistanceMatrixRequest(coords,ids, mode,city):

	#convert coords to string

	coordString= ''
	for crd in coords:
		crdString = str(crd[0]) + ',' + str(crd[1]) 
		coordString += crdString + '|'
	coordString = coordString[:-1]
	url = 'http://maps.googleapis.com/maps/api/distancematrix/xml?origins='+ coordString + '&destinations=' + coordString + '&mode='+str(mode)+'&sensor=false'
	url2 = utils.createSecureURL(url)
	print url2
	#xml = requests.get(url2)
	response = urllib2.urlopen(url2)
	xml = response.read()
	parseDistanceMatrix(xml, ids,mode,city)



def queryWithDistanceMatrix(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/transportation/'
	jsonVals = open(basePath + 'block_groups_processed.geojson','r')
	geojsonData = geojson.load(jsonVals)
	idToCenters = {}

	for feat in geojsonData['features']:
		[lng, lat] = feat['properties']['center']
		shape_id = feat['id']
		idToCenters[shape_id] = (lat, lng)

	#output_file = open(basePath + mode+ '_values.csv', 'a+')
	coords = []
	ids = []
	for i in range(1,20):
		coords.append(idToCenters[i])
		ids.append(i)
	makeDistanceMatrixRequest(coords,ids,'bicycling',city)


def handleErrors():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Manhattan/transportation/'
	errors = open(basePath + 'errors.csv', 'r').readlines()

	for error in errors:
		err = error.split(',')
		id1 = int(err[0])
		id2 = int(err[1])
		mode = err[2][:-1]
		spotQuery('Manhattan', mode, id1,id2)







def toShapelyPoly(processCoords):
	# print len(processCoords)
	# if len(processCoords) ==1 :
	# 	coords = processCoords[0]
	# else:
	# 	coords = processCoords

	# if len(coords) ==1 :
	# 	coordsSelect = coords[0]
	# else:
	# 	coordsSelect = coords

	# shapelyCoords =[]
	print len(processCoords)
	for crds in processCoords:
		shapelyCoords.append((crds[0], crds[1]))
	polygon = Polygon(shapelyCoords)
	return polygon

def processBoulderBGs():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Boulder/transportation/'
	boundaryGIS = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Boulder/boundary.geojson','r')
	boundaryGJS = geojson.load(boundaryGIS)
	boundary_shapes = []

	for boundary_feat in boundaryGJS['features']:
		processCoords = boundary_feat['geometry']['coordinates'][0]
		poly_shape = toShapelyPoly(processCoords)
		boundary_shapes.append(poly_shape)

	print boundary_shapes, len(boundary_shapes)



	blockGroupsGIS = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Boulder/bg_candidates.geojson','r')
	blockGroupsGJS = geojson.load(blockGroupsGIS)
	features = []
	i_d = 1
	for bg_feat in blockGroupsGJS['features']:
		geometry = bg_feat['geometry']
		
		centerLat = float(bg_feat['properties']['INTPTLAT'])
		centerLng = float(bg_feat['properties']['INTPTLON'])
		center = [centerLng, centerLat]
		area = bg_feat['properties']["ALAND"]
		inBoulder = False
		centerPoint = Point(centerLng, centerLat)
		for boundary_shape in boundary_shapes:
			if boundary_shape.contains(centerPoint):
				inBoulder = True

		if inBoulder:
			shape_id = int(i_d)
			properties = {"center":center, "area":area}
			feature = geojson.Feature(geometry=geometry, properties=properties, id=shape_id)
			features.append(feature)
			i_d +=1

	print i_d
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'block_groups_processed_new2.geojson','w')
	output_file.write(geojson_data)





def processNYCroads():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Manhattan/'
	roadsGIS = open(basePath + 'roads.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	for feat in roadsGJS['features']:
		roadType = feat['properties']['FEAT_DESC']
		if roadType == 'Paved Road' or roadType == 'Paved  Road':
			newFeature = geojson.Feature(geometry=feat['geometry'], properties={'name':feat['properties']['NAME']})
			features.append(newFeature)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'roads_processed.geojson','w')
	output_file.write(geojson_data)


def processSMroads():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/SantaMonica/'
	roadsGIS = open(basePath + 'roads.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	types  = []
	for feat in roadsGJS['features']:
		roadType = feat['properties']['TYPE']
		types.append(roadType)
		if roadType == "STREET" or roadType == "FREEWAY":
			newFeature = geojson.Feature(geometry=feat['geometry'], properties={'name':feat['properties']['FULLNAME']})
			features.append(newFeature)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'roads_processed.geojson','w')
	output_file.write(geojson_data)

	print set(types)


def processBOCroads():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Boulder/'
	roadsGIS = open(basePath + 'roads.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	for feat in roadsGJS['features']:
			newFeature = geojson.Feature(geometry=feat['geometry'], properties={'name':feat['properties']['LABEL_NAME']})
			features.append(newFeature)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'roads_processed.geojson','w')
	output_file.write(geojson_data)



def processSFroads():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/San Francisco/'
	roadsGIS = open(basePath + 'streets.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	types = []
	accept = ["RD", "EXPY", "BLVD", "DR", "STWY", "HWY", "EXPY", "WAY", "ST", "AVE"]
	for feat in roadsGJS['features']:
		if feat['properties']['ST_TYPE'] in accept:
			newFeature = geojson.Feature(geometry=feat['geometry'])
			features.append(newFeature)
	#print set(types)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'roads_processed.geojson','w')
	output_file.write(geojson_data)

def processPORroads():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Portland/'
	roadsGIS = open(basePath + 'streets.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	types = []
	accept = ["RD", "BLVD", "HWY", "ST", "AVE"]
	for feat in roadsGJS['features']:
		typ = feat['properties']['FTYPE']
		if typ in accept:
			newFeature = geojson.Feature(geometry=feat['geometry'])
			features.append(newFeature)
	#print set(types)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'roads_processed.geojson','w')
	output_file.write(geojson_data)

def processDC():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Washington/'
	roadsGIS = open(basePath + 'waterbodies.geojson','r')
	roadsGJS = geojson.load(roadsGIS)
	features = []
	length = []
	#accept = ["RD", "BLVD", "HWY", "ST", "AVE"]
	for feat in roadsGJS['features']:
		leng = feat['properties']['SHAPE_Area']
		length.append(leng)
		if leng > 400:
			newFeature = geojson.Feature(geometry=feat['geometry'])
			features.append(newFeature)
	print set(length)
	featureColleciton = geojson.FeatureCollection(features)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'waterbodies_processed.geojson','w')
	output_file.write(geojson_data)

#processPORroads()
#processSFroads()
#processSMroads()
#processNYCroads()

#processBoulderBGs()



#processDC()
#queryWithDistanceMatrix('Manhattan')


# spotQuery('Manhattan', 'driving', 110,120)
# spotQuery('Manhattan', 'driving', 110,130)
# spotQuery('Manhattan', 'driving', 110,200)
# spotQuery('Manhattan', 'driving', 110,220)

# spotQuery('Manhattan', 'transit', 110,120)
# spotQuery('Manhattan', 'transit', 110,130)
# spotQuery('Manhattan', 'transit', 110,200)
# spotQuery('Manhattan', 'transit', 110,220)

# spotQuery('Manhattan', 'bicycling', 110,120)
# spotQuery('Manhattan', 'bicycling', 110,130)
# spotQuery('Manhattan', 'bicycling', 110,200)
# spotQuery('Manhattan', 'bicycling', 110,220)

#loadGeoJSON('Chicago')
csvToJSON('Chicago')
#handleErrors()

#blockQuery('Manhattan', 'driving',280)
#blockQuery('Portland', 'bicycling',0)


#blockQuery('Manhattan', 'transit',280)


#processNHoodnames()
#jsonToGeoJSON()
#segmentDistance()
#controller('Manhattan','driving',37 ,62)
#loadGeoJSON('Philadelphia')