import json

import datetime as datetime
import pdf2txt
import pyPdf
import StringIO


def readData():
	rawdata = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Portland/portland_data_2012.txt', 'r')
	rawdata = rawdata.readlines()

	jsonData = [[],[], [], []]
	streetData = {'2010':{},'2011':{}, '2012':{}, '2013':{}}
	i = 0

	for line in rawdata:
		print i
		i+=1
		line = line.split(',')
		crashID = line[0]

		[latDegrees, latMin, latSec]  = [line[25], line[26], line[27]]
		[lngDegrees, lngMin, lngSec]  = [line[28], line[29], line[30]]

		if [latDegrees, latMin, latSec] != ['', '', ''] and [lngDegrees, lngMin, lngSec] != ['', '', '']:
			lat = float(latDegrees) + float(latMin)/60 + float(latSec)/3600
			# -1 to account for West lng
			lng = (float(lngDegrees) * -1) + float(lngMin)/60 + float(lngSec)/3600
			lng = lng *-1

			year = line[10]


			obj = {}
			obj['year'] = year
			obj['lat'] = lat
			obj['lng'] = lng

			street1 = line[33].strip()
			street2 = line[34].strip()

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

			obj['street1'] = street1
			obj['street2'] = street2
			obj['crashID'] = crashID
			
			obj['noAccidents'] = 1
			jsonData[int(year[3])].append(obj)

	jsonOpt = 	{'city': 'Portland', 'accidents':{'2010': jsonData[0], '2011':jsonData[1], '2012':jsonData[2], '2013': jsonData[3]}, 'clusters': streetData}
	jsonFile = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Portland/final_data.json'
	jsonOutput = json.dumps(jsonOpt)
	outFile = open(jsonFile, 'w')
	outFile.write(jsonOutput)
	outFile.close()



def readWithStreetNames():
	pdfFile = "/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Portland/data_with_streetnames.pdf"
	pdf = pyPdf.PdfFileReader(open(pdfFile,"rb"))
	pageCount=0
	for text in pdf.pages:
		print "processing.." + str(pageCount) + " out of " + str(len(pdf.pages))
		txt = text.extractText()
		pageText = txt.replace(u"\xa0", " ")
		pageStartIndex = 0
		pageEndIndex = 0
		# for i in range(len(txt)):
		# 	if 'FranciscoPrimary' in txt[i]:
		# 		pageStartIndex=i
		# 	if 'InfoPage' in txt[i]:
		# 		pageEndIndex = i
		print pageText

	# pdfContent = StringIO(getPDFContent(pdfFile).encode("ascii", "ignore"))
	# for line in pdfContent:
	# 	print line.strip()

readWithStreetNames()

#readData()