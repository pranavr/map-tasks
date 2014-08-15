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


def csvToJSON(city):
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/' + str(city) +'/transportation/'
	valuesToJSON = {}
	PARKING_TIME = 0


	modes = ['driving','transit']

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

	 		if mode =='transit':
	 			duration += 10

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


	
	maxValue = -100000
	minValue = 1000000
	finalJSON = {}

	for id1 in valuesToJSON:
		if id1 != 'ranges':
			maxValue = -100000
			minValue = 1000000
			for id2 in valuesToJSON[id1]:
				if id1 != id2:
					driving = valuesToJSON[id1][id2]['modes']['driving']
					transit = valuesToJSON[id1][id2]['modes']['transit']

					if transit > 10.0:
						value = driving/transit
					else:
						value = 0.0

					if value > maxValue:
						maxValue = value

					if value < minValue:
						minValue = value

			valuesToJSON[id1]['max'] = maxValue

	#print maxValue, minValue

	maxRound = -10000
	minRound = 100000

	print maxValue

	for id1 in valuesToJSON:
		if id1 != 'ranges':
			for id2 in valuesToJSON[id1]:
				if id1 != id2 and id2 != 'max':
					driving = valuesToJSON[id1][id2]['modes']['driving']
					transit = valuesToJSON[id1][id2]['modes']['transit']

					if transit > 10.0:
						value = driving/transit
					else:
						value = 0.0
					normalized = value / valuesToJSON[id1]['max']

					roundedFinal = float("%.2f" % normalized)
					roundedFinal = roundedFinal * 10

					#print roundedFinal
					#print value, maxValue, roundedFinal, normalized

				else:
					roundedFinal = 0.0

				if roundedFinal > maxRound and roundedFinal <10.0:
					maxRound = roundedFinal

				if roundedFinal < minRound:
					minRound = roundedFinal


				if id1 in finalJSON:
					finalJSON[id1][id2] = roundedFinal
				else:
					finalJSON[id1] ={id2: roundedFinal}

				if id2 in finalJSON:
					finalJSON[id2][id1] = roundedFinal
				else:
					finalJSON[id2] ={id1: roundedFinal}


	finalJSON['ranges'] = {'efficiency': [minRound,  maxRound]}
	#print finalJSON
	highest = -10
	highestID = 0
	lowest = 100000
	edgeIds = [313,662,134,86,460,329,135,549,251,252,419,157,418]
	for id1 in finalJSON:
		if id1 != 'ranges':
			total = 0
			count = 0
			for id2 in finalJSON[id1]:
				if id1 in edgeIds:
					finalJSON[id1][id2] = 2.0
				
				if finalJSON[id1][id2] > 0.0:

					total += finalJSON[id1][id2]
					count+=1

			if count ==0:
				avg = total/len(finalJSON.keys())
			else:
				avg = total/count


			if avg > highest and id1 not in edgeIds:
				highest = avg
				highestID = id1

			if avg < lowest:
				lowest = avg

			finalJSON[id1]['avg'] = avg

	finalJSON['best'] = highestID
	print highestID
	finalJSON['ranges']['avg'] = [lowest,highest]

	jsonValues = json.dumps(finalJSON)
	output_file = open(basePath + 'efficiency_values_drtr10.json','w')
	output_file.write(jsonValues)






csvToJSON('Brooklyn')
