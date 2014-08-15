import urllib2
import utils as utils
import xml.etree.cElementTree as et
from bs4 import BeautifulSoup
import requests
import time

def brooklyn_segments_read():
	url = 'http://www.brooklyn.com/intersections.php'
	intersections = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Brooklyn/intersections.txt','w')
	website = urllib2.urlopen(url)
	html = website.read()
	soup = BeautifulSoup(html)
	a_tags = soup.find_all("a",href=True)
	for a in a_tags:
		href_url = a['href']
		location = href_url.split('T=')[1]
		print href_url, location
		intersections.write(str(location) + '\n')



def geocode_segments():
	intersections = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Brooklyn/intersections.txt','r').readlines()
	segmentpoints = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Brooklyn/segment_points.txt','a+')
	segments = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Brooklyn/segments.txt','a+')
	errors = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Brooklyn/segment-errors.txt','a+')
	count = 3594
	while (count < len(intersections)):
	 	intersection = intersections[count]
		url = 'https://maps.googleapis.com/maps/api/geocode/xml?address='
		[street1, street2] = intersection.split('and')
		url += str(''.join(street1.split()))
		url += 'and'
		url += str(''.join(street2[:len(street2)-1].split()))
		url += '+Brooklyn,+NY&sensor=false'

		#'&key=AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4'
		secureURL = utils.createSecureURL(url)
		#print secureURL
		
		xml = requests.get(url)
		[lat,lng] = getLatLng(xml.content)
		if lat != None and lng != None:
			print lat, lng
			print "done with " + str(count) + " out of " + str(len(intersections))
			segmentpoints.write(str(lat) +','+str(lng)+'\n')
			segments.write(intersection[:len(intersection)-1]+',' + str(lat)+','+str(lng)+'\n')
		else:
			errors.write(intersection)

		count+=1
		time.sleep(0.7)

def getLatLng(response):
	parse = et.XML(response)
	if (parse.find('status').text == 'OK'):
		if (parse.find("result").find("type").text =='intersection'):
			location = parse.find("result").find("geometry").find("location")
			lat = float(location.find("lat").text)
			lng = float(location.find("lng").text)
			return [lat,lng]
		else:
			return [None,None]
	else:
		return [None,None]

def extract_intersections(osm, verbose=True):
    # This function takes an osm file as an input. It then goes through each xml 
    # element and searches for nodes that are shared by two or more ways.
    # Parameter:
    # - osm: An xml file that contains OpenStreetMap's map information
    # - verbose: If true, print some outputs to terminal.
    # 
    # Ex) extract_intersections('WashingtonDC.osm')
    #
    tree = et.parse(osm)
    root = tree.getroot()
    counter = {}
    output = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Austin/segment_points.csv','a+')
    for child in root:
        if child.tag == 'way':
            for item in child:
                if item.tag == 'nd':
                    nd_ref = item.attrib['ref']
                    if not nd_ref in counter:
                        counter[nd_ref] = 0
                    counter[nd_ref] += 1

    # Find nodes that are shared with more than one way, which
    # might correspond to intersections
    intersections = filter(lambda x: counter[x] > 1,  counter)

    # Extract intersection coordinates
    # You can plot the result using this url.
    # http://www.darrinward.com/lat-long/
    intersection_coordinates = []
    i = 0
    total = len(root)
    for child in root:
        if child.tag == 'node' and child.attrib['id'] in intersections:
            coordinate = child.attrib['lat'] + ',' + child.attrib['lon']
            if verbose:
                print coordinate
                print "done with "+ str(i) + " out of " + str(total)
                i+=1
            output.write(coordinate + '\n')
            intersection_coordinates.append(coordinate)

    
    return intersection_coordinates


#brooklyn_segments_read()
geocode_segments()
#osm = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Austin/austin.osm'
#extract_intersections(osm)