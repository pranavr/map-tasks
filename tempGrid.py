import utils as utils


def cambridgeGrid(topLeft, bottomRight, numPoints):
	output = open('/Users/pranavramkrishnan/Desktop/Research/maps/static/data/Cambridge/skyprints_grid.csv', 'w')
	output.write('lat,lng'+'\n')
	grid = utils.makeGrid(topLeft, bottomRight, numPoints)
	for pt in grid:
		output.write(str(pt[0]) + ',' + str(pt[1]) + '\n')

	print "done"


def checkGrid():
	grid = open('/Users/pranavramkrishnan/Desktop/final_skyprints_grid.csv', 'r')
	grid = grid.readlines()
	processed = []
	for pt in grid:
		print pt
		processed.append((float(pt[0]), float(pt[1])))

	print len(processed)
	print len(set(processed))


checkGrid()