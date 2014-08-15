
import urllib
import urllib2
import time
import requests
import utils as utils
import sys
import json



def downloadImage(lattitude, longitude,heading,pitch, outputfile, api_key='AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4'):
	url = 'http://maps.googleapis.com/maps/api/streetview?size=800x800&location='+str(lattitude)+','+str(longitude)+'&fov=120&heading='+str(heading)+'&pitch='+str(pitch)+'&sensor=false'
	url = utils.createSecureURL(url)
	response = requests.get(utils.createSecureURL(url))
	localfile = open(str(outputfile), 'w')
   	
   	localfile.write(response.content)
   	localfile.close()


def downloadStreetViews(place):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(place) + '/'
	jsonData = json.load(open(basePath + 'final_data2.json', 'r'))
	accidents = jsonData['accidents']
	streetData = jsonData['streets']
	clusters_data = jsonData['clusters']
	accidents_with_images = []
	outputfilename = basePath + '/bicycle_accidents/streetviews/'
	i = 0
	while  i < len(accidents):
		acc  = accidents[i]
		lat = acc['lat']
		lng = acc['lng']
		acc['image_id'] = i
		filename = outputfilename + place + '_' + str(i) + '.jpeg'
		downloadImage(lat, lng, 0, 0, filename)
		print 'done with ' + str(i) + ' out of ' + str(len(accidents)-1)
		i +=1
		accidents_with_images.append(acc)
		time.sleep(0.3)


	outputfile = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(place) + '/bicycle_accidents/final_data2.json', 'w')
	finalJSON = {'city':place, 'accidents':accidents_with_images, 'streets':streetData, 'clusters':clusters_data}
	json.dump(finalJSON, outputfile)


print sys.argv[1]
downloadStreetViews(sys.argv[1])



