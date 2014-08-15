import requests
#import findImages as helper
import utils as utils
import math
import time
import datetime
import random
import geojson
import json
import xml.etree.cElementTree as et
from shapely.geometry import shape, Point, LineString, Polygon
from PIL import Image
from StringIO import StringIO
import colorsys



def readJSON(city):
	gvals = open('static/data/'+str(city)+'/greenery.json', 'r')
	data = json.load(gvals)
	rawData = {}
	print len(data)
	for d in data:
		latlng = (data[d][0], data[d][1])
		
		rawData[latlng] = [data[d][2], data[d][3]]
	
	output = open('static/data/'+str(city)+'/greenery.csv', 'w')	
	for d in rawData.keys():
		print d[0], d[1], rawData[d][0], rawData[d][1]
		output.write(str(d[0]) +','+str(d[1]) +',' +str(rawData[d][0]) +','+ str(rawData[d][1]) + '\n')



def toGeoJSON(city):
	green_values = open('static/data/'+str(city)+'/greenery.csv', 'r')
	green_values = green_values.readlines()
	features = []
	for i in range(1, len(green_values)):
		gv = green_values[i].split(',')
		point = geojson.Point((float(gv[0]), float(gv[1])))
		prop = {"opacity": float(gv[2]), "radius":float(gv[3])}
		feature = geojson.Feature(geometry=point, properties=prop, id=i)
		features.append(feature)

	featureColleciton = geojson.FeatureCollection(features)
	print featureColleciton
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open('static/data/'+str(city)+'/greenery.geojson','w')
	output_file.write(geojson_data)

def clean_points(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city) + '/'
	greenery = json.load(open(basePath+'green/greenery.geojson','r'))
	boundary = json.load(open(basePath+'boundary.geojson','r'))
	boundary_shape = shape(boundary['features'][0]['geometry'])
	cambridge_features = []

	for point in greenery['features']:
		point_shape = Point(point['geometry']['coordinates'][1],point['geometry']['coordinates'][0])
		if boundary_shape.contains(point_shape):
			cambridge_features.append(point)

	featureCollection = geojson.FeatureCollection(cambridge_features)
	geojson_data = geojson.dumps(featureCollection)
	output_file = open(basePath+ '/green/greenery2.geojson','w')
	output_file.write(geojson_data)

def getImages(point, bearing, api_key='AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4'):

	query_url = 'http://maps.googleapis.com/maps/api/streetview?'

	latitude = point[0]
	longitude = point[1]
	location = str(latitude)+' '+str(longitude)
	#print(location)
	
	headings = [(bearing + 90 + 10) % 360, (bearing - 90 - 10) % 360]
	orientation = ['left', 'right']
	values = []
	for i in range(len(headings)):
		current_heading = headings[i]
		current_pitch = 0
		url2 = 'http://maps.googleapis.com/maps/api/streetview?size=50x50&location='+str(latitude)+','+str(longitude)+'&fov=110&heading='+str(current_heading)+'&pitch='+str(current_pitch)+'&sensor=false'
		secureURL = utils.createSecureURL(url2)
			#print ("heading = "+ str(current_heading)+ " pitch = "+ str(current_pitch))
			#print "URL = " + str(url2)

		
		response = requests.get(secureURL)
		#parse = et.XML(response.content)
		#print str(parse)


		[greenVal, [R, G, B]] = processImage(response.content)
		values.append([greenVal, [R, G, B]])
			# localfile = open('images/cambridge/'+str(name)+'_'+str(orientation[i]) + '_'+str(lattitude)+'_'+str(longitude)+ '_'+ '.jpeg', 'w')
	
			# localfile.write(response.content)
			# localfile.close()
		#outputFile.write(str(lattitude) + ',' + str(longitude) + ',' + str(values) + '\n')
	print secureURL
	return values

def processImage(image):
	img = Image.open(StringIO(image)).convert("RGB")
	#img.show()
	R_count , G_count, B_count = 0, 0 ,0
	height, width = img.size
	for i in range(height):
		for j in range(width):
			r, g, b = img.getpixel((i,j))
			h, s, v = colorsys.rgb_to_hsv(r/255.0,g/255.0,b/255.0)
			pixel_color = get_pixel_color(h,s,v)
			#print r,g,b,h* 360,s * 100,v * 100, pixel_color
			if pixel_color == 'red':
				R_count +=1
			if pixel_color == 'blue':
				B_count +=1
			if pixel_color =='green':
				G_count +=1

	#print height, width
 	num_pixels = float(height * width)
	img_green_value = float(G_count)/num_pixels

	return [img_green_value, [R_count, G_count, B_count]]

def get_pixel_color(h,s,v):
    #h from 0-360, s and v from 0-100
    h = h * 360
    s = s* 100
    v = v*100
    if v < 25: return 'black'
    if s < 15: return None
    if h < 10: return 'red'
    if 75 < h < 100: return 'green'
    if 210 < h < 230: return 'blue'
    return None



def process_values(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city) + '/'
	greenery = json.load(open(basePath+'green/greenery2.geojson','r'))
	csv = open(basePath + 'green/locations.csv', 'a+')
	radii = []
	count = 0

	misses = [(42.3923164451, -71.1461732451), (42.3541092657, -71.1024612476), (42.3714731065, -71.1132207351), (42.3997190373, -71.1304608654), (42.3816325179, -71.1207984099), (42.388917823, -71.1183665027), (42.388852855, -71.125067115), (42.3830568375, -71.1349497196), (42.3687665577, -71.1169101016), (42.3652459742, -71.0923812041), (42.362539202, -71.0937018092), (42.3742730326, -71.1363473293), (42.3701696631, -71.1133346053), (42.377515, -71.131606), (42.3985686, -71.1362478)]
	
	while (count < len(misses)):
		#point = greenery['features'][count]
		lat = misses[count][0]
		lng = misses[count][1]
		url = 'https://maps.googleapis.com/maps/api/geocode/xml?latlng=' 
		url += str(lat)
		url += ','
		url += str(lng)
		url += '&sensor=false'
		secureURL = utils.createSecureURL(url)
		response = requests.get(secureURL)
		parse = et.XML(response.content)
		if parse.find('status').text =='OK':
			address = parse.find('result').find('formatted_address').text

			address_components = parse.find('result').findall('address_component')
			short_street = ''
			long_street = ''

			for addr in address_components:
				if addr.find('type') != None and addr.find('type').text == 'route':
					short_street = addr.find('short_name').text
					long_street = addr.find('long_name').text
					print short_street,long_street
			address = address.encode('utf8')
			csv.write(str(lat) + ';' + str(lng) + ';' + str(long_street) + ';' + str(address) + '\n')
			print secureURL
			print "done with ......" + str(count) + ' out of ' + str(len(greenery['features']))

		count+=1
		time.sleep(0.5)

def capitalize_name(street):
	names = street.split()
	newname = ''
	for name in names:
		newname += name.capitalize()
		newname += ' '
	return newname.rstrip()

import ast
def create_street_segments(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city) + '/'
	streets = json.load(open(basePath+'streets2.json','r'))
	features = []


	output = open(basePath + 'segs_test.csv', 'w')
	main_output = open(basePath + 'green/query_points2.csv', 'w')
	coordinates_list = []
	check = {}
	types = []
	types_to_ignore = ["EXPY","FWY", "TER","ALY","HWY", "I","KYS","GRN", "Fwy", "PROMENADE",None]
	query_points = []

	ds = []

	for feature in streets['features']:
		st_type = feature['properties']['STREETTYPE']
		types.append(st_type)
		if st_type not in types_to_ignore:
			name = feature['properties']['REGISTERED'] 
			name += ' ' 
			name += str(st_type)
			street_name = capitalize_name(name)
			# CNN = str(feature['properties']['CNN'])
			# F_NODE = float(feature['properties']["F_NODE_CNN"])
			# T_NODE = float(feature['properties']["T_NODE_CNN"])
			coordinates = feature['geometry']['coordinates']
			i = 0
			#total_dist = 0
			while (i < len(coordinates)-1):
			 	start_coord = (float(coordinates[i][0]), float(coordinates[i][1]))
			 	end_coord = (float(coordinates[i+1][0]), float(coordinates[i+1][1]))

			 	seg_dist = utils.compute_distance([start_coord[1], start_coord[0]], [end_coord[1], end_coord[0]]) * 5280
				ds.append(seg_dist)
			 	if seg_dist > 75:
			 		query_points.append([truncate_float(start_coord[1]), truncate_float(start_coord[0]), truncate_float(end_coord[1]), truncate_float(end_coord[0]),street_name])

				i+=1

	print set(types)
	print min(ds), max(ds), sum(ds)/len(ds)

	for pt in query_points:
		line = ''
		for s in pt:
			line+= str(s)
			line+=','
		main_output.write(line+'\n')

	points = {'segments':query_points, 'streets':[]}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/greenery_test_test.json','w')
	output_file.write(final_json_data)




def get_value_controller(city, count):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city) + '/'
	segments = open(basePath + 'green/query_points.csv', 'r').readlines()
	
	output_file = open(basePath + 'green/greenData.csv', 'a+')
	error_file = open(basePath + 'green/greenData-errors.csv', 'a+')
	#count = 9500

	while (count < len(segments)):
		pt = segments[count].split(',')
		start  = [float(pt[0]), float(pt[1])]
		end = [float(pt[2]), float(pt[3])]

		coords = [start,end]
		bearing = utils.compute_bearing(start,end)
		for point in coords:
			img_values =  getImages(point,bearing)
			print img_values[0]
			if img_values[0][1] == [0,0,0] or img_values[1][1]==[0,0,0]:
				error_file.write(str(count) + ';' + str(point[1]) + ';' + str(point[0]) + ';' + str(pt) + '\n')
				print "error at " + str(count)
			else:
				time.sleep(0.25)
				output_file.write(str(point[1]) + ';' + str(point[0]) + ';' + str(img_values) +  ';' + str(pt) +'\n')
		
		print "done with " + str(count) + " out of " + str(len(segments))
		count+=1
		






def match_address_interpolate_values():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/'
	greenData = json.load(open(basePath+'green/greenery2.geojson','r'))
	addrs = open(basePath + 'green/locations.csv', 'r').readlines()

	address_book = {}
	i = 0
	while (i < len(addrs)):
	 	addr = addrs[i]
		address = addr.split(';')
		address_book[(float(address[0]), float(address[1]))] = [str(address[2]), str(address[3])]
		i+=1
	
	#print len(address_book.keys())
	missed = []

	for feature in greenData['features']:
		coordinates = (feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][1])
		if coordinates in address_book:
			feature['properties']['street'] = address_book[coordinates][0]
		else:
			missed.append(coordinates)

	streets = {}
	values = {}
	for feature in greenData['features']:
		street = feature['properties']['street']
		coordinates = (feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][1])
		if street in streets:
			streets[street].append(coordinates)
		else:
			streets[street] = [coordinates]

		values[coordinates] = [feature['properties']['radius'], feature['properties']['opacity']]

	interpolated_values = {}
	street_values = {}

	for street in streets:
		avg_values = []
		processed_street = process_street(streets[street], values)
		for coord in processed_street.keys():
			interpolated_values[coord] = [processed_street[coord]]
			avg_values.append(processed_street[coord][1])
		street_values[street] = sum(avg_values)/len(avg_values)
	
	jsonData = []
	radius_list = []
	op_list = []
	avg_check = []
	json_streets =[]
	for feature in greenData['features']:
		coordinates = (feature['geometry']['coordinates'][0], feature['geometry']['coordinates'][1])
		#print interpolated_values[coordinates]
		final_radius = interpolated_values[coordinates][0][0]
		final_opacity = interpolated_values[coordinates][0][1]
		feature['properties']['radius'] = final_radius
		radius_list.append(final_radius)
		op_list.append(final_opacity)
		feature['properties']['opacity'] = final_opacity
		street = feature['properties']['street']
		avg_check.append(street_values[street])
		jsonData.append([coordinates[0],coordinates[1], street,final_radius, final_opacity])
		json_streets.append([street, street_values[street]])

	print min(avg_check), max(avg_check), sum(avg_check)/len(avg_check)
	
	points = {'points':jsonData, 'streets':json_streets}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/greenery4.json','w')
	output_file.write(final_json_data)


def findExtremeWest(cluster):
	xMin = 10000
	iMin = -1
	# xMax = 0
	# iMax = -1
	for i in range(len(cluster)):
		if cluster[i][0] <= xMin:
			xMin = cluster[i][0]
			iMin = i

		# if cluster[i][0] >= xMax:
		# 	xMax = cluster[i][0]
		# 	iMax = i

	#print cluster, iMin, cluster[iMin]
	return [iMin, cluster[iMin]]

def process_street(street, values):
	sorted_street = []
	processed_street = {}
	i = 0
	street_copy = street
	#print "1 = " ,len(street)
	sorted_street = sorted(street,key=lambda x:x[0])

	i = 1
	#print "2 = ", len(sorted_street)
	processed_street[sorted_street[0]] = values[sorted_street[0]]
	while (i < len(sorted_street)-1):
		left_val_r, left_val_o = values[sorted_street[i-1]]
		this_val_r, this_val_o = values[sorted_street[i]]
		right_val_r, right_val_o = values[sorted_street[i+1]]

		val_r = 0.3 * left_val_r + 0.3 * this_val_r +  0.3 *right_val_r 
		val_o = 0.3 * left_val_o + 0.3 * this_val_o + 0.3 * right_val_o

		processed_street[sorted_street[i]] = [val_r, val_o]
		i+=1

 	processed_street[sorted_street[-1]] = values[sorted_street[-1]]
 	return processed_street

def process_streets_geojson():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/'
	lines = json.load(open(basePath+'roads.geojson','r'))
	data = json.load(open(basePath+'green/greenery4.json','r'))
	print data.keys()
	streets = data['streets']
	i_d = 0
	reduced_features = []
	st_types = []
	short_to_full = {
		'Ln':'Lane',
		'Rd':'Road',
		'Hill':'Hill',
		'Way':'Way',
		'Pk':'Park',
		'Pl':'Place',
		'St N':'Street',
		'Mews':'Mews',
		'Hwy':'Highway',
		'Dr':'Drive',
		'Sq':'Square',
		'Tpk':'Turnpike',
		'St':'Street',
		'Cir':'Circle',
		'Ext':'Extension',
		'Pkwy':'Parkway',
		'Aly':'Alley',
		'Blvd':'Boulevard',
		'Ave':'Avenue',
		'Ter':'Terrace',
		'Ct':'Court',
		'Row':'Row',
		None:''
	}	
	for feature in lines['features']:
		street_name = feature['properties']['Street_Nam']
		street_name += ' '
		street_name += short_to_full[feature['properties']['Street_Typ']]
		street_name = street_name.rstrip()
		street_geom = feature['geometry']
		if street_name in streets:
			avg_value = streets[street_name]
		else:
			print street_name
		reduced_features.append(geojson.Feature(geometry=street_geom, properties={'street':street_name, 'value':avg_value}, id=i_d))
		i_d+=1

	featureCollection = geojson.FeatureCollection(reduced_features)
	geojson_data = geojson.dumps(featureCollection)
	output_file = open(basePath+ '/streetlines.geojson','w')
	output_file.write(geojson_data)

def consolidate_data(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/'
	gdata = open(basePath + 'green/greenData.csv','r').readlines()

	jsonData = []
	vals = []


	segment_values = {}
	row = 0
	for gline in gdata:
		print gline
		gline = gline.split(';')
		values = gline[2].split(',')
		green_left = float(values[0][2:])
		green_right = float(values[4][2:])
		lng = float(gline[0])
		lat = float(gline[1])
		meta_data = gline[3].split(',')
		start_lng = float(meta_data[0][2:-1])
		start_lat = float(meta_data[1][2:-1])
		end_lng = float(meta_data[2][2:-1])
		end_lat = float(meta_data[3][2:-1])
		street = meta_data[4][2:-1]
		
		
		final_green = (green_left + green_right)/2

		jsonData.append([start_lat, start_lng, end_lat, end_lng,street,final_green])

		row+=1


	points = {'segments':jsonData,'streets':[]}
	final_json_data = json.dumps(points, )
	output_file = open(basePath+ '/green/greenery_consolidated.json','w')
	output_file.write(final_json_data)


def segment_control(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/'
	gdata = open(basePath + 'green/greenData-errors.csv','r').readlines()
	output = json.load(open(basePath + 'green/greenery4.json','r'))
	jsonData = output['points']
	for feat in gdata:
		feat = feat.split(';')
		data = feat[3].split(',')
		start_lng = float(data[0][2:-1])
		start_lat = float(data[1][2:-1])
		end_lng = float(data[2][2:-1])
		end_lat = float(data[3][2:-1])
		name = data[4][2:-1]
		jsonData.append([start_lat,start_lng, end_lat,end_lng,name,0.05,0.05])

	avgs = []

	for pt in jsonData:
		v1 = pt[5]
		v2 = pt[6]
		avgs.append((v1 +v2)*0.5)

	print min(avgs), max(avgs), sum(avgs)/len(avgs)	
	points = {'segments':jsonData,'streets':[]}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/greenery_test.json','w')
	output_file.write(final_json_data)

def truncate_float(val):
	return "%.6f" % val

def dummy_segments():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/San Francisco/'
	streets = json.load(open(basePath + 'streets.geojson','r'))
	jsonData = []
	types_to_ignore = ["RAMP", "ALY", "TUNL", "HWY", "None", "NONE", 'STPS', None]
	for feature in streets['features']:
		st_type = feature['properties']['ST_TYPE']
		if st_type not in types_to_ignore:
			name = feature['properties']['STREET'] 
			name += ' ' 
			name += str(st_type)
			street_name = capitalize_name(name)
			CNN = str(feature['properties']['CNN'])
			F_NODE = float(feature['properties']["F_NODE_CNN"])
			T_NODE = float(feature['properties']["T_NODE_CNN"])
		
		coordinates = feature['geometry']['coordinates']
		i = 0
		
		while (i < len(coordinates)-1):
		 	start_coord = (coordinates[i][0], coordinates[i][1])
		 	end_coord = (coordinates[i+1][0], coordinates[i+1][1])
		 	jsonData.append([start_coord[1], start_coord[0], end_coord[1], end_coord[0],name, 0.5, 0.5])
		 	i+=1

	points = {'points':jsonData,'streets':[]}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/greenery_test_all.json','w')
	output_file.write(final_json_data)

def cambridge_specials():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/'
	streets = json.load(open(basePath + 'streets.geojson','r'))
	gdata = open(basePath + 'green/greenData-errors.csv','r').readlines()
	output = open(basePath + 'green/re_queries.csv','a+')
	segments = []
	for feature in streets['features']:
		st_type = feature['properties']['Street_Typ']
		name = feature['properties']['Street_Nam']
		if name =='Broadway':
			if st_type == None:
				print name, st_type
				CNN = str(feature['properties']['ID'])
				coordinates = feature['geometry']['coordinates']
				F_NODE = float(feature['properties']["FromNode"])
				T_NODE = float(feature['properties']["ToNode"])
				i = 0
				#total_dist = 0
				while (i < len(coordinates)-1):
				 	start_coord = (coordinates[i][0], coordinates[i][1])
				 	end_coord = (coordinates[i+1][0], coordinates[i+1][1])

					segments.append([start_coord[0], start_coord[1], end_coord[0], end_coord[1],name,CNN,F_NODE,T_NODE,st_type])
					i+=1
	for gd in gdata:
		gd = gd.split(';')
		val = gd[3].split(',')
		print float(gd[1]), float(gd[2]), float(val[0][2:-1]), float(val[1][2:-1])
		segments.append([float(gd[1]), float(gd[2]), float(val[0][2:-1]), float(val[1][2:-1]), val[4][2:-1], val[5][2:-1], val[6][2:-1], val[7][2:-1], val[8][2:-1]])


	for segment in segments:
		print segment
		line = ''
		for s in segment:
			line += str(s)
			line += ','
		output.write(line +'\n')


def street_averages(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/'
	segments = json.load(open(basePath + '/green/greenery_consolidated.json','r'))['segments']
	streets = {}

	for segment in segments:
		street = segment[4]
		print segment
		green_value = (float(segment[5]))
		if street in streets:
			streets[street].append(green_value)
		else:
			streets[street] = [green_value]
	avgs = []

	for segment in segments:
		values = streets[segment[4]]
		street_average = sum(values)/len(values)
		avgs.append(sum(values)/len(values))
		segment.append(street_average)

	street_data = []

	for st in streets.keys():
		street_data.append([st, sum(streets[st])/len(streets[st])])

	print min(avgs), max(avgs), sum(avgs)/len(avgs)
	points = {'segments':segments,'streets':street_data}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/greenery5.json','w')
	output_file.write(final_json_data)


def compress_data(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) + '/'
	segments = json.load(open(basePath + 'green/greenery5.json','r'))['segments']
	compressed_segments= []
	catch_duplicates = {}
	street_list = {}
	street_values = {}
	for segment in segments:
		s_lat = "%.6f" % segment[0]
		s_lng = "%.6f" % segment[1]
		e_lat = "%.6f" % segment[2]
		e_lng = "%.6f" % segment[3]


		street = segment[4]
		street_list[street] = 1
		value = segment[5]

		if street in street_values:
			street_values[street].append(value)
		else:
			street_values[street] = [value]

		if ((s_lat, s_lng),(e_lat,e_lng)) in catch_duplicates:
			catch_duplicates[((s_lat, s_lng),(e_lat,e_lng))].append(value)
		else:
			catch_duplicates[((s_lat, s_lng),(e_lat,e_lng))] = [s_lat, s_lng,e_lat, e_lng,street,value]

	street_list_comp = street_list.keys()
	street_mapping = {}
	reverse_mapping = {}
	avgs = []

	for i in range(len(street_list_comp)):
		sname = street_list_comp[i]
		street_mapping[sname] = i
		
		street_avg = sum(street_values[sname])/len(street_values[sname])
		reverse_mapping[i] = [sname,float("%.5f" % street_avg)]
		avgs.append(street_avg)



	for singleton in catch_duplicates.keys():
		if len(catch_duplicates[singleton]) ==6:
			catch_duplicates[singleton].append(catch_duplicates[singleton][-1])
		

	values = []
	for sing in catch_duplicates.keys():
		s_v = catch_duplicates[sing]
		v1 = float("%.3f" % s_v[5])
		v2 = float("%.3f" % s_v[6])
		values.append(v1)
		values.append(v2)
		street = street_mapping[s_v[4]]
		seg = [float(s_v[1]),float(s_v[0]),float(s_v[3]),float(s_v[2]),street,v1, v2]
		print seg
		compressed_segments.append(seg)


	print min(values),max(values), sum(values)/len(values)
	print min(avgs),max(avgs), sum(avgs)/len(avgs)

	points = {'segments':compressed_segments}
	s_map_json = json.dumps(reverse_mapping, separators=(',',':'))
	final_json_data = json.dumps(points, separators=(',',':'))
	output_file = open(basePath+ 'green/greenery_compressed.json','w')
	map_file = open(basePath + 'green/street_map_compressed.json','w')
	output_file.write(final_json_data)
	map_file.write(s_map_json)


def SF_residual():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/San Francisco/'
	all_file = json.load(open(basePath + '/green/greenery_test_all.json','r'))['points']
	my_file = json.load(open(basePath + '/green/greenery4.json','r'))['segments']
	#requeries = open(basePath + 'green/re_queries.csv','a+')
	wish = open(basePath + 'green/dreamworks.json','w')
	wish_list = []
	my_segments = {}

	for my_seg in my_file:
		s_lat= "%.7f" % my_seg[0]
		s_lng = "%.7f" % my_seg[1]
		e_lat = "%.7f" % my_seg[2]
		e_lng = "%.7f" % my_seg[3]
		my_segments[((s_lat, s_lng), (e_lat, e_lng))] = my_seg
		wish_list.append([s_lat, s_lng, e_lat,e_lng])


	residual_count=0

	for a_seg in all_file:
		s_lat_a= "%.7f" % a_seg[0]
		s_lng_a = "%.7f" % a_seg[1]
		e_lat_a = "%.7f" % a_seg[2]
		e_lng_a= "%.7f" % a_seg[3]
		name = capitalize_name(a_seg[4])

		if ((s_lat_a, s_lng_a), (e_lat_a, e_lng_a)) not in my_segments:
			residual_count+=1
			line = s_lat_a + ','+ s_lng_a + ',' + e_lat_a + ',' + e_lng_a + ',' +name 
			wish_list.append([s_lat_a,s_lng_a, e_lat_a, e_lng_a])
			#requeries.write(line+'\n')

	print len(my_segments.keys()), residual_count
	points = {'segments':wish_list,'streets':[]}
	final_json_data = json.dumps(points)
	output_file = open(basePath+ '/green/dreamworks.json','w')
	output_file.write(final_json_data)




def atlanta_streets_extraction():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Atlanta/'
	#boundary = json.load(open(basePath + 'boundary.geojson','r'))

	boundary_shape = Polygon([(-84.34994,33.82137), (-84.34994,33.70749), (-84.44435,33.70749), (-84.44435,33.82137)])
	all_features = json.load(open(basePath + 'allstreets.geojson','r'))['features']
	accept_types = ['Way','Pt','Ln','Rd','Pl', 'Roadway', 'Dr', 'Sq', 'St', 'Cir', 'Pkwy',
	 'Loop', 'Esplanade', 'Arc', 'Driveway','Blvd','Ave', 'Ct']
	streets = []
	for feature in all_features:
		line = []
		line_coords = feature['geometry']['coordinates']
		# for line in line_coords:
		# 	print len(line)
			# coord_line = []
			# for crd in line:
			# 	print crd
			# 	coord_line.append([float(crd[1]),float(crd[0])])
			# line.append(coord_line)
		if type(line_coords[0][0]) == type(0.55):
			line_shape = LineString(line_coords)
			
			if boundary_shape.contains(line_shape):
				streets.append(feature)
		else:
			for lineSeg in line_coords:
				line_shape2 = LineString(lineSeg)

				if boundary_shape.contains(line_shape2):
					streets.append(feature)
	print len(streets)

	featureCollection = geojson.FeatureCollection(streets)
	geojson_data = geojson.dumps(featureCollection)
	output_file = open(basePath+ '/streets.geojson','w')
	output_file.write(geojson_data)


def just_cambridge_streets():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/green/'
	segments = json.load(open(basePath + 'greenery_compressed.json','r'))
	street_map =  json.load(open(basePath + 'street_map_compressed.json','r'))
	output = open(basePath + 'streets.csv','w')

	for seg in segments['segments']:
		output.write(str(seg[0]) + ',' +str(seg[1]) + ',' + str(seg[2]) + ',' + str(seg[3]) + ',' + street_map[str(seg[4])][0] + '\n')


just_cambridge_streets()
#get_value_controller("Portland",89603)
#get_value_controller("Washington",21775)

#atlanta_streets_extraction()
#compress_data('Portland')
#dummy_segments()
#SF_residual()
#get_value_controller("Portland",34306)
#get_value_controller_2("San Francisco")
#consolidate_data('Portland')
#street_averages('Portland')
#cambridge_specials()
#segment_control('San Francisco')
#dummy_segments()

#process_streets_geojson()
#match_address_interpolate_values()
#create_street_segments('Washington')

#process_values('Cambridge')
#clean_points('Cambridge')
#toGeoJSON('Cambridge')