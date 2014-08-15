import json
import os
import time
import requests
import utils as utils
import xml.etree.cElementTree as et


def createJSON(city):
	filepath = '/Users/pranavramkrishnan/Desktop/Research/NYC-bikedata/' + str(city) + '/'  
	#output_csv = open('/Users/pranavramkrishnan/Desktop/Research/NYC-bikedata/raw_data/' + str(city)+'_data.csv', 'w')
	files = os.listdir(filepath)
	json_tag = '_mnacc.json'
	jsonData = [[]]
	year = '2013'
	streetData = {}

	#output_csv.write('year,month,lat,lng,street1,street2,injury_count' +'\n')
	grand_total = 0
	error_count = 0
	for fl in files:
		month_json_file = filepath + fl
		month_json = json.load(open(month_json_file, 'r'))
		date = month_json['date_context']
		month_count = 0
		clean_count = 0

		for data in month_json['intersection_list']:
			injury_count = data["injury_count"]
			
			if 'cyclists' in injury_count.keys():
				month_count +=1
				jsonObj = {}
				lat = data['lat_long'][0]
				lng = data['lat_long'][1]
				jsonObj['lat'] = lat
				jsonObj['lng'] = lng
				injury_count = injury_count['cyclists']
				address = data['name'].split('and')
				[street1, street2] = address


				if (len(str(lat))!=0 or len(str(lng))!=0) and (lat != 'None' or lng != 'None') and (lat != None or lng != None):
					pass
				else:
					[lat,lng] = geocode_point(street1.rstrip(),street2.rstrip(), city)
					print 'geolocated', lat,lng
					time.sleep(0.3)



				if (lat != 'None' or lng != 'None') and (lat != None or lng != None):
					clean_count +=1

					jsonObj['street1'] = str(street1)
					jsonObj['street2'] = str(street2)

					jsonData[0].append(jsonObj)	

					[month, year] = date.split()
					#output_csv.write(year+',' + month + ',' +str(lat)+','+str(lng)+','+str(street1)+','+str(street2)+','+str(injury_count)+'\n')

					#print lat,lng
					if not (street1 == '(N/A)' or street1 == None or street1 =='(UNK)'):
						if street1 not in streetData:
							streetData[street1] = [[float(lat), float(lng)]]
						else:
							streetData[street1].append([lat, lng])

					if not (street2 == '(N/A)' or street2 == None or street2 == '(UNK)'):
						if street2 not in streetData:
							streetData[street2] = [[float(lat), float(lng)]]
					else:
						streetData[street2].append([float(lat), float(lng)])
		
		grand_total += month_count
		error_count += (month_count - clean_count)


		#print date, ' ', str(month_count), ' ', str(clean_count), ' ', str(month_count - clean_count)
	print city, ' ', grand_total, ' ', error_count

	outputfile = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' +str(city)+'/bicycle_accidents/final_data_2013.json', 'w')
	finalJSON= {'city':str(city), 'accidents': jsonData[0], 'streets': streetData}
	json.dump(finalJSON, outputfile)


def geocode_point(street1, street2, city,state='NY	'):
	url = 'https://maps.googleapis.com/maps/api/geocode/xml?address='
	url += str(street1)
	url += 'and'
	url += str(street2)
	url += '+'+str(city)+',+'+str(state)+'&sensor=false'

	url = url+'&key=AIzaSyBZnvqy9HEpG-LAQwm_AxDOegMciI9jgP4'
	#secureURL = utils.createSecureURL(url)
	print url
	
	xml = requests.get(url)
	[lat,lng] = getLatLng(xml.content)
	if lat != None and lng != None:
		return [lat, lng]
	else:
		print 'error'
		return [lat, lng]

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


#createJSON('Brooklyn') 
#createJSON('Manhattan')
#createJSON('Bronx')
#createJSON('Queens')
createJSON('Staten Island')