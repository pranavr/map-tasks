import openpyxl as px

import urllib
import urllib2
import xml.etree.cElementTree as et
import requests
import datetime
import hmac 
import base64
import hashlib
import urlparse	
import time
import geojson as json
#import pdf2txt.py

def readXLSXdata():
	W = px.load_workbook('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Los Angeles/2010 to 2013 all Accident Data.xlsx', use_iterators=True)
	sheets = W.get_sheet_names()
	sheet = W.get_sheet_by_name(name=sheets[0])
	data = []
	for row in sheet.iter_rows():
		if (row[0].internal_value != 'RD'):
			type1 = int(row[2].internal_value)
			location = row[5].internal_value
			[streetNo, street1, street2] = processLocation(location)
			# streetNo = row[5].internal_value
			# street1 = row[6].internal_value
			# street2 = row[7].internal_value
			noAccidents = 1
			date = row[3].internal_value.strip()
			# type1 = row[3].internal_value
			# type2 = row[4].internal_value

			#if (type1.strip() == 'Bicycle' or type2.strip() == 'Bicycle'):
			#print type1, type(type1)

			if (type1 == 3008 or type1 == 3016 or type1 == 3603):
				#print streetNo, street1, street2,noAccidents,date
				data.append([streetNo, street1,street2,noAccidents,date])

	return data


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




def processLocation(location):
	output = []
	if '/' in location:
		location = location.split('/')
		output = ['', str(location[0]), str(location[1])]
	else:
		location = location.split()
		output = [str(location[0]), str(location[1]), '(N/A)']

	#print output
	return output

def streetString(street):
	string = ''
	for s in street:
		string += str(s)
		string += '+'
	return string[:len(string)-1]

def geoLocate(data):
	out = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Los Angeles/geolocated_data.txt', 'a+')
	latLngs = []
	i = 1433
	while (i < len(data)):
		[streetNo, street1,street2,noAccidents,date] = data[i]
		print str(i) + " of " + str(len(data))
		
		time.sleep(1)
		addrStr = ''
		if streetNo == '':
			str1 =  street1.split()
			str2 = street2.split()
			addrStr += streetString(str1)
			addrStr += '+and+'
			addrStr += streetString(str2)
			addrStr += ',+'
		else:
			str1 = street1.split()
			addrStr += str(streetNo)
			addrStr += ','
			addrStr += streetString(str1)
			addrStr += ',+'

		addrStr += 'Los Angeles,+CA'
		baseUrl = 'http://maps.googleapis.com/maps/api/geocode/xml?address='
		endParams = '&sensor=false&client=gme-mitisandt'


		#url = urlparse.urlparse(baseUrl + addrStr + endParams)
		#url = createSecureURL(url)
		url = baseUrl + addrStr + "&sensor=false"

		xml  = requests.get(url,verify=False)

		print "URL = " + str(url)
		parse = et.XML(xml.content)
		

		if parse.find('status').text =='OK':
			lat = parse.find('result').find('geometry').find('location').find('lat').text
			lng = parse.find('result').find('geometry').find('location').find('lng').text
			address = parse.find('result').find('formatted_address').text
			print [lat,lng]
			latLngs.append([lat,lng])
			address = address.encode('utf8')
			print address
			out.write(str(streetNo) +';' + str(address) + ';' + str(street1) + ';' + str(street2) + ';' + str(noAccidents) + ';' + str(date) + ';'+ str(lat) + ';'+ str(lng) + '\n')
			i+=1
		else:
			print 'RequestERROR' + parse.find('status').text


	return latLngs


def getYear(date):
	date = date.split('/')
	return '20' + str(date[2])

def createJSON():
	data = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Los Angeles/geolocated_data.txt', 'r')
	data = data.readlines()
	

	jsonData = [[],[], [], []]
	streetData = {'2010':{},'2011':{}, '2012':{}, '2013':{}}
	for line in data:
		line = line.split(';')
		obj = {}

		obj['date'] = str(line[5])
		year = getYear(str(line[5]))
		obj['year'] = year

		lat = float(line[6])
		lng = float(line[7])

		obj['lat'] = lat
		obj['lng'] = lng

		street1 = str(line[2]).upper().strip()
		street2 = str(line[3]).upper().strip()

		if (street1 == '' or street1== None):
			street1 = '(N/A)'

		if (street2 == '' or street2== None):
			street2 = '(N/A)'

		if not (street1 == '(N/A)' or street1 == None or street1 =='(UNK)'):
			if street1 not in streetData[year].keys():
				streetData[year][street1] = [[lat, lng]]
			else:
				streetData[year][street1].append([lat, lng])

		if not (street2 == '(N/A)' or street2 == None or street2 == '(UNK)'):
			if street2 not in streetData[year].keys():
				streetData[year][street2] = [[lat, lng]]
			else:
				streetData[year][street2].append([lat, lng])

		obj['address'] = str(line[1])
		obj['street1'] = street1
		obj['street2'] = street2
		
		obj['noAccidents'] = 1
		jsonData[int(year[3])].append(obj)

		print obj
	
	jsonOpt = 	{'city': 'Los Angeles', 'accidents':{'2010': jsonData[0], '2011':jsonData[1], '2012':jsonData[2], '2013': jsonData[3]}, 'clusters': streetData}
	jsonFile = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Los Angeles/final_data.json'
	jsonOutput = json.dumps(jsonOpt)
	outFile = open(jsonFile, 'w')
	outFile.write(jsonOutput)
	outFile.close()

#readXLSXdata()
createJSON()
#data = readXLSXdata()
#geoLocate(data)