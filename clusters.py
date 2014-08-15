import json
import math
import utils



def createClusters(street, threshold_dist):
	i= 1
	clusters = [[street[0]]]
	while (i < len(street)):
		print str(i) + " out of " + str(len(street))
		if street[i] != [None, None]:
			closestClusterIndex = findClosestCluster(street[i], clusters, threshold_dist)

			if closestClusterIndex != -1:
				clusters[closestClusterIndex].append(street[i])
			else:
				clusters.append([street[i]])
		i += 1

	finalClusters = []
	for cluster in clusters:
		if len(cluster) >= 3:
			[west,east] = findEndPoints(cluster)
			if [west, east] != None:
				finalClusters.append([west,east])
	
	return finalClusters

def findClosestCluster(point, clusters, threshold_dist):
	bestMin = 10000
	bestIndex = -1
	for i in range(len(clusters)):
		avgPoint = clusters[i]
		dist = computeDistance(point, average(clusters[i]))
		if dist <= threshold_dist:
			if dist <= bestMin:
				bestMin = dist
				bestIndex = i

	return bestIndex


def computeDistance(p1, p2):
	[p1x, p1y] = [float(p1[0]), float(p1[1])]
	[p2x, p2y] = [float(p2[0]), float(p2[1])]
	return math.pow((math.pow((p2y-p1y),2) + math.pow((p2x - p1x),2)),0.5)
			

def average(cluster):
	sumX = 0
	sumY = 0
	for pt in cluster:
		sumX += float(pt[0])
		sumY += float(pt[1])
	return [sumX/len(cluster), sumY/len(cluster)]



def findEndPoints(cluster):
	if len(cluster) >= 2:
		[west, east] = findExtremeWestEast(cluster)
		return [west, east]
	else:
		return None



def findExtremeWestEast(cluster):
	xMin = 10000
	iMin = -1
	xMax = 0
	iMax = -1
	for i in range(len(cluster)):
		if cluster[i][0] <= xMin:
			xMin = cluster[i][0]
			iMin = i

		if cluster[i][0] >= xMax:
			xMax = cluster[i][0]
			iMax = i
	return [cluster[iMin], cluster[iMax]]






