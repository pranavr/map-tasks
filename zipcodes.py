import json
import geojson

def processNYregions():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/zipcodes/'
	filename = basePath + 'TEST_data.json'
	jsonData = json.load(open(filename, 'r')) 
	zipcode_initial = {}

	ny_geojson = geojson.load(open(basePath+'nyzipcodes.json','r'))
	ny_regions = ny_geojson['features']

	for zipcode in jsonData:
		numCompanies = len(jsonData[zipcode])

		#inefficient but works
		for region in ny_regions:
			if str(region['properties']['ZCTA']) == str(zipcode):
				region['properties']['numCompanies'] = numCompanies

	featureColleciton = geojson.FeatureCollection(ny_regions)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'ny_zip_regions.geojson','w')
	output_file.write(geojson_data)


def processCountries():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/zipcodes/'
	filename = basePath + 'manhattan_byzip.json'
	jsonData = json.load(open(filename, 'r')) 
	

	# world_geojson = geojson.load(open(basePath+'world.geojson','r'))
	# country_list =[]

	# for country in world_geojson["features"]:
	# 	name = country["properties"]["name"]
	# 	country_list.append(name)

	final_json = {}
	for zipcode in jsonData:
		jurisdiction_initial = {}
		print zipcode
		for data_pt in jsonData[zipcode]:
			#jurisdiction = jsonData[zipcode]['jurisdiction']
			for z in jsonData[zipcode]:

				jurisdiction =  str(z['jurisdiction'])

				if jurisdiction in jurisdiction_initial.keys():
					jurisdiction_initial[jurisdiction] +=1
				else:
					jurisdiction_initial[jurisdiction] = 1

		final_json[str(zipcode)] = jurisdiction_initial

	# featureColleciton = geojson.FeatureCollection(ny_regions)
	# geojson_data = geojson.dumps(featureColleciton)
	json_data = json.dumps(final_json)
	output_file = open(basePath + 'zip_to_country.json','w')
	output_file.write(json_data)


def combineGeoJSONS():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/zipcodes/'
	world_geojson = geojson.load(open(basePath+'world.geojson','r'))
	countries = world_geojson["features"]
	filtered= []
	for country in countries:
		if str(country["properties"]["name"]) != "United States":
			filtered.append(country)

	us_states_geojson = geojson.load(open(basePath+'us_states.geojson','r'))
	states = us_states_geojson["features"]
	for state in states:
		state["properties"]["name"] = state['properties']['NAME']
		filtered.append(state)


	featureColleciton = geojson.FeatureCollection(filtered)
	geojson_data = geojson.dumps(featureColleciton)
	output_file = open(basePath + 'world_filtered.geojson','w')
	output_file.write(geojson_data)


def zipCountryCounts():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/zipcodes/'
	data = open(basePath+'zip_jur_count.csv','r').readlines()
	jsonValues = {}
	maxValues = {}
	for val in data:
		val = val.split(',')
		[zipcode, region, count] = [str(val[0]), str(val[1]), int(val[2])]
		region = region.replace(' ', '_')
		if zipcode in jsonValues.keys():
			jsonValues[zipcode]['values'][region]=count
			maxValues[zipcode].append(count)
			jsonValues[zipcode]['regions'].append(region)
		else:
			jsonValues[zipcode] = {'values': {region:count}, 'regions':[region]} 
			maxValues[zipcode] = [count]

	
	for zipcode in maxValues.keys():
		jsonValues[zipcode]['max'] = max(maxValues[zipcode])


	json_data = json.dumps(jsonValues)
	output_file = open(basePath + 'zip_region_counts.json','w')
	output_file.write(json_data)


def region_to_zip():
	basePath = '/Users/pranavramkrishnan/Desktop/Research/maps/static/data/zipcodes/'
	data = open(basePath+'zip_jur_count.csv','r').readlines()
	jsonValues = {}
	maxValues = {}

	for val in data:
		val = val.split(',')
		[zipcode, region, count] = [str(val[0]), str(val[1]), int(val[2])]
		region = region.replace(' ', '_')
		if region in jsonValues.keys():
			jsonValues[region]['values'][zipcode]=count
			maxValues[region].append(count)
			jsonValues[region]['zipcodes'].append(zipcode)
		else:
			jsonValues[region] = {'values': {zipcode:count}, 'zipcodes':[zipcode]}
			maxValues[region] = [count]

	
	for region in maxValues.keys():
		jsonValues[region]['max'] = max(maxValues[region])


	json_data = json.dumps(jsonValues)
	output_file = open(basePath + 'region_zip_counts_updated.json','w')
	output_file.write(json_data)


zipCountryCounts()
