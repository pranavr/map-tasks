import math
import urllib
import urllib2
from PIL import Image
from StringIO import StringIO
import requests
import fileinput
#from google.directions import GoogleDirections


################################# Helpers #################


CAR_LENGTH = 0.005

def degrees_to_radians(degrees):
	return degrees * math.pi /180;

def radians_to_degrees(radians):
	return radians  *  180 / math.pi


def compute_distance(p1, p2):
	[lat1, long1] = p1
	[lat2, long2] = p2
	degree_to_radians = math.pi/180
	dist_to_miles = 3960
	dist_to_kms = 6371.01

	#phi = 90 - latitude
	phi1 = (90.0 - lat1)* degree_to_radians
	phi2 = (90.0 - lat2)* degree_to_radians

	#theta = longitude
	theta1 = long1*degree_to_radians
	theta2 = long2*degree_to_radians

	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1-theta2) + math.cos(phi1)*math.cos(phi2))
	arc = math.acos(cos)

	return arc * dist_to_miles


############################################################



def compute_street_distance(p1, p2):
	gd = GoogleDirections('AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4')

	a = ''+str(p1[0])+','+str(p1[1])
	b = ''+str(p2[0])+','+str(p2[1])
	res = gd.query(a,b)
	d = res.distance

	print res.response
	#d = compute_distance([42.372218,-71.098979],[42.37183,-71.098522])
	#print "distance = "+ str(d)
	return d


#compute_street_distance([42.369333,-71.100996],[42.370895,-71.099891])




def compute_bearing(pointA, pointB):

	#from https://gist.github.com/jeromer/2005586

    lat1 = degrees_to_radians(pointA[0])
    lat2 = degrees_to_radians(pointB[0])
    
    diffLong = degrees_to_radians(pointB[1] - pointA[1])
    
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
                                           * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    initial_bearing = radians_to_degrees(initial_bearing)
    compass_bearing =  (initial_bearing + 360) % 360
    return compass_bearing


def compute_offset(startPoint, distance, bearing):
	lat = startPoint[0]
	lng = startPoint[1]

	# in miles. divide by 6371.01for kms
	distRatio = distance/ 3960

	distSine = math.sin(distRatio)
	distCosine = math.cos(distRatio)


	bearing = degrees_to_radians(bearing)
	startLatRad = degrees_to_radians(lat)
	startLngRad = degrees_to_radians(lng)
	startLatCos = math.cos(startLatRad)
	startLatSin = math.sin(startLatRad)

	endLatRads = math.asin((startLatSin * distCosine) + (startLatCos * distSine * math.cos(bearing)))
	endLonRads = startLngRad + math.atan((math.sin(bearing) * distSine * startLatCos)/(distCosine - startLatSin * math.sin(endLatRads)));


	finalLat = radians_to_degrees(endLatRads)
	finalLng = radians_to_degrees(endLonRads)


	

	return [finalLat, finalLng]

#b = compute_bearing([42.369333,-71.100996],[42.370895,-71.099891])
#compute_offset([42.369333,-71.100996], 0.2,  b )


def getImages(segments, bearing, name, outputFile, api_key='AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4'):

	query_url = 'http://maps.googleapis.com/maps/api/streetview?'

	for s in range(len(segments)):
		seg = segments[s]
		lattitude = seg[0]
		longitude = seg[1]
		location = str(lattitude)+' '+str(longitude)
		#print(location)
		
		headings = [(bearing + 90) % 360, (bearing - 90) % 360]
		orientation = ['left', 'right']
		values = []
		for i in range(len(headings)):
			current_heading = headings[i]
			current_pitch = -10
			url2 = 'http://maps.googleapis.com/maps/api/streetview?size=400x400&location='+str(lattitude)+','+str(longitude)+'&fov=120&heading='+str(current_heading)+'&pitch='+str(current_pitch)+'&sensor=false&key='+api_key
   			#print ("heading = "+ str(current_heading)+ " pitch = "+ str(current_pitch))
   			#print "URL = " + str(url2)


   			response = requests.get(url2)
   			[greenVal, [aR, aG, aB]] = processImage(response.content)
   			values.append([greenVal, [aR, aG, aB]])
   			# localfile = open('images/cambridge/'+str(name)+'_'+str(orientation[i]) + '_'+str(lattitude)+'_'+str(longitude)+ '_'+ '.jpeg', 'w')
   	
   			# localfile.write(response.content)
   			# localfile.close()
   		outputFile.write(str(lattitude) + ',' + str(longitude) + ',' + str(values) + '\n')

###################################################################



def processImage(image):
	img = Image.open(StringIO(image)).convert("RGB")
	greenPixels = 0
	averageR , averageG, averageB = 0, 0 ,0
	height, width = img.size
	for i in range(height):
		for j in range(width):
			r, g, b = img.getpixel((i,j))
			averageB += b
			averageG += g
			averageR += r

			greenvalue = g - r/2 - b/2
			if greenvalue > 50:
				greenPixels += 1

 	numPixels = float(height * width)
	imgGreen = float(greenPixels)/numPixels
	return [imgGreen, [averageR/numPixels, averageG/numPixels, averageB/numPixels]]






def segment_street(startCoordinates, endCoordinates, bearing):
	# startCoordinates = intersections[startIntersection]
	# endCoordinates = intersections[endIntersection]

	# print "St = " + str(startCoordinates)
	# print "end = " + str(endCoordinates)

	streetLength = compute_distance(startCoordinates, endCoordinates)
	streetBearing = compute_bearing(startCoordinates, endCoordinates)

	# print "streetLength = " + str(streetLength)
	numSegments = math.ceil(streetLength/10)
	#print numSegments

	start = startCoordinates
	sections = [startCoordinates]
	segLength = 20
	if (bearing <= 90):
		#print "bearing = " + str(bearing) + "loop 1"
		while ((start[0] <= endCoordinates[0]) and (start[1] <=endCoordinates[1])):
			next = compute_offset(start,CAR_LENGTH, streetBearing)
			sections.append(next)
			start = next

	elif (bearing > 90 and bearing <= 180):
		#print "bearing = " + str(bearing) + "loop 2"
		while ((start[0] >= endCoordinates[0]) and (start[1] <=endCoordinates[1])):
			next = compute_offset(start,CAR_LENGTH, streetBearing)
			sections.append(next)
			start = next
	elif (bearing > 180 and bearing <= 270):
		#print "bearing = " + str(bearing) + "loop 3"
		while ((start[0] >= endCoordinates[0]) and (start[1] >=endCoordinates[1])):
			next = compute_offset(start,CAR_LENGTH, streetBearing)
			sections.append(next)
			start = next

	elif (bearing > 270 and bearing <=360):
		#print "bearing = " + str(bearing) + "loop 4"
		while ((start[0] <= endCoordinates[0]) and (start[1] >=endCoordinates[1])):
			next = compute_offset(start,CAR_LENGTH, streetBearing)
			sections.append(next)
			start = next


	#print "done with loop"
	#print sections
	return sections

def controller():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/San Francisco/'
	f = open( basePath + 'final_segments_no_dups2.csv', 'r')
	# file_complete = open('static/data/San Francisco/green/complete_sanfrancisco.txt', 'r+')
	# file_2 = open('static/data/San Francisco/green/complete_sanfrancisco.txt','a+')
	outputFile = open( basePath + 'green/query_points.csv', 'w')
	streets = []

	lines = f.readlines()
	#complete_lines = file_complete.readlines()
	num = len(lines)
	count = 0
	while(count < len(lines)):
		line = lines[count]
		#print "LINE = " + line
		# if line in complete_lines:
		# 	print "complete " + str(count) + " out of " + str(num)

		# else:

		line2 = line.split(",")
		name = line2[0]
		#print str(line2)
		street_name = str(line2[0])
		lat1 = float(line2[1])
		lng1 = float(line2[2])
		lat2 = float(line2[3])
		lng2 = float(line2[4])
		#print line

		startCoordinates = [lat1, lng1]
		endCoordinates = [lat2, lng2]
		streetBearing = compute_bearing(startCoordinates, endCoordinates)
		segments = segment_street(startCoordinates, endCoordinates, streetBearing)
		#getImages(segments, streetBearing, name, outputFile)
		for s in range(len(segments)):
			seg = segments[s]
			latitude = seg[0]
			longitude = seg[1]
			outputFile.write(str(street_name) + ',' + str(latitude) +',' + str(longitude) + ',' + str(streetBearing) + '\n')
		
		print "done with street " + name + " .... " + str(count) + " out of " + str(num)


		#file_2.write(line)
		#line.strip()

		count +=1

controller()




