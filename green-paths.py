import requests
#import findImages as helper
import utils as utils
import math
import random
import json



def readJSON(city):
	gvals = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/green/greenery_compressed.json', 'r')
	streets = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/green/street_map_compressed.json', 'r')
	output = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/'+str(city)+'/green/paths/data.csv', 'a+')
	green_data = json.load(gvals)
	smap = json.load(streets)
	rawData = {}
	seg_greens = []
	seg_dists = []
	for segment in green_data['segments']:
		startLat = float(segment[0])
		startLng = float(segment[1])
		endLat = float(segment[2])
		endLng = float(segment[3])
		segmentID = str(segment[4])
		segmentGreen = smap[segmentID][1]
		if startLat == endLat and startLng == endLng:
			segmentDist = 0.0
		else:
			segmentDist = utils.compute_distance([startLat, startLng], [endLat,endLng])
		seg_greens.append(segmentGreen)
		seg_dists.append(segmentDist)
		output.write(str(startLat) +','+str(startLng) +','+ str(endLat) +','+str(endLng) + ',' + str(segmentGreen) +','+ str(segmentDist) + '\n')




def coordinateToNode(lat,lng):
	node = str(lat) + ',' + str(lng)
	#print node
	return node



def computeWeight(green,dist):
	ALPHA = 10
	BETA = 5
	return (ALPHA * green) - (BETA * dist)


def fixFloats(value):
	return "%.5f" % float(value)

def buildGraph():
	data = 	open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/green/paths/data.csv', 'r')
	segments = data.readlines()

	graph = {}

	for segment in segments:
		segValues = segment.split(',')
		[startLat, startLng] = [fixFloats(segValues[0]), fixFloats(segValues[1])]
		[endLat, endLng] = [fixFloats(segValues[2]), fixFloats(segValues[3])]
		print startLat
		if startLat < 42.37097 :
			print "here"
			nodeA = coordinateToNode(startLat, startLng)
			nodeB = coordinateToNode(endLat, endLng)
			greenValue = float(segValues[4])
			distValue = float(segValues[5])
			weight = computeWeight(greenValue, distValue)

			if nodeA in graph:
				graph[nodeA].append([nodeB,weight])
			else:
				graph[nodeA] = [[nodeB, weight]]

			if nodeB in graph:
				graph[nodeB].append([nodeA,weight])
			else:
				graph[nodeB] = [[nodeA, weight]]

	return graph


def BFS(start,end):
	graph = buildGraph()
	queue = [[start]]
	print graph, queue
	while len(queue) > 0:
		print "working on BFS"
		path = queue.pop(0)
		#print path
		lastnode = path[-1]
		
		if lastnode == end:
			print 'path Found!!', path
			return path

		adjacent_nodes = graph[lastnode]

		for [ad_node,val] in adjacent_nodes:
			new_path = list(path)
			new_path.append(ad_node)
			queue.append(new_path)





start = '42.39912,-71.14075'

end = '42.37289,-71.13444'

#readJSON('Cambridge')
#buildGraph()

BFS(start,end)

















