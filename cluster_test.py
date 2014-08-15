
import random

def createClusters():
	street = [19, 100, 98,97, 1,2, 10, 13, 3, 14, 15, 18, 31, 45, 47, 65,66, 67, 17]
	#street = [1,3,5]
	current= 1
	minDist = 3
	clusters = [[street[0]]]
	while (current < len(street)):
		closestClusterIndex = findClosestCluster(street[current], clusters)
		if (abs(street[current] - average(clusters[closestClusterIndex])) < minDist):
			clusters[closestClusterIndex].append(street[current])
		else:
			clusters.append([street[current]])
		current = current + 1

	print clusters


def findClosestCluster(point, clusters):
	bestCluster = []
	bestDist = 100000
	for i in range(len(clusters)):
		cluster = clusters[i]
		dist = abs(point - average(cluster))
		if dist <= bestDist:
			bestDist = dist
			bestCluster = i
	return bestCluster

def average(cluster):
	return sum(cluster)/len(cluster)
	

createClusters()