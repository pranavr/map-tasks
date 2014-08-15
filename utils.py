import math
import random
import urlparse
import base64
import hmac
import hashlib

def compute_offset(startPoint, distance, bearing):
	lat = startPoint[0]
	lng = startPoint[1]

	# in miles. divide by 6371.01for kms
	distRatio = distance/ 3960
	distRatio = distRatio

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

# def makeGrid(topLeft, bottomRight, numPoints):
# 	topLat = topLeft[0]
# 	leftLng = topLeft[1]
# 	bottomLat = bottomRight[0]
# 	rightLng = bottomRight[1]
# 	horizontal_offset = (compute_distance(topLeft, [topLat, rightLng])/numPoints)
# 	vertical_offset = (compute_distance(topLeft, [bottomLat, leftLng])/numPoints)
# 	print horizontal_offset, vertical_offset

# 	pointer = topLeft
# 	rowheader = topLeft
# 	grid = [pointer]
# 	for i in range(numPoints):
# 		for j in range(numPoints):
# 			if (i==49 and j == 49	): print str(pointer[0]) + ',' + str(pointer[1])
# 			next = compute_offset(pointer, horizontal_offset, 90)	
# 			grid.append(next)
#  			pointer = next

# 		rowheader = compute_offset(rowheader, vertical_offset, 180)
# 		pointer = rowheader

# 	print grid
# 	return grid


def createSecureURL(url):

	url = url + '&client=gme-mitisandt'
	url = urlparse.urlparse(url)
	urlToSign = url.path + "?" + url.query
	#print urlToSign
	privateKey = '7HyrvDsrV6trC91E-E7F6xpjWjs='
	decodedKey = base64.urlsafe_b64decode(privateKey)
	signature = hmac.new(decodedKey, urlToSign, hashlib.sha1)
	encodedSignature = base64.urlsafe_b64encode(signature.digest())
	originalUrl = url.scheme + '://' + url.netloc + url.path + "?" + url.query
	fullURL = originalUrl + "&signature=" + encodedSignature
	#print "URL = " + fullURL
	return fullURL


def segment_street(startCoordinates, endCoordinates, bearing, car_length):
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
			next = compute_offset(start,car_length, streetBearing)
			sections.append(next)
			start = next

	elif (bearing > 90 and bearing <= 180):
		#print "bearing = " + str(bearing) + "loop 2"
		while ((start[0] >= endCoordinates[0]) and (start[1] <=endCoordinates[1])):
			next = compute_offset(start,car_length, streetBearing)
			sections.append(next)
			start = next
	elif (bearing > 180 and bearing <= 270):
		#print "bearing = " + str(bearing) + "loop 3"
		while ((start[0] >= endCoordinates[0]) and (start[1] >=endCoordinates[1])):
			next = compute_offset(start,car_length, streetBearing)
			sections.append(next)
			start = next

	elif (bearing > 270 and bearing <=360):
		#print "bearing = " + str(bearing) + "loop 4"
		while ((start[0] <= endCoordinates[0]) and (start[1] >=endCoordinates[1])):
			next = compute_offset(start,car_length, streetBearing)
			sections.append(next)
			start = next


	#print "done with loop"
	#print sections
	return sections

#makeGrid([40.833297, -74.032935], [40.543290, -73.722571], 50)
	