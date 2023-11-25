#!/usr/bin/env python
# -*- coding: utf8

# osm2maproulette
# Converts OSM elements in geojson format to MapRoulette cooperative input file
# Usage: osm2maproulette <inputfile.geojson>


import json
import sys
import base64
import urllib.request
from xml.etree import ElementTree as ET


version = "0.2.0"



# Output message

def message (output_text):

	sys.stdout.write (output_text)
	sys.stdout.flush()



# Create osmChange file for feature

def create_osmchange_xml(feature, osm_id):

	xml_root = ET.Element("osmChange", version="0.6")

	xml_action = ET.Element("create")
	xml_root.append(xml_action)

	osm_id -= 1 
	point = feature['geometry']['coordinates']
	xml_element = ET.Element("node", id=str(osm_id), lat=str(point[1]), lon=str(point[0]))
	xml_action.append(xml_element)

	for key, value in iter(feature['properties'].items()):
		xml_element.append(ET.Element("tag", k=key, v=value))

	osmchange = ET.tostring(xml_root, encoding="utf-8", method="xml", xml_declaration=True)  # Returns bytes
#	osmchange = osmchange.replace(b">", b">\n")

	return osmchange



# Extend geojson feature for MapRoulette cooperative challenge

def convert_element(feature, osm_id):

	osmchange = create_osmchange_xml(feature, osm_id)  # bytes
	osmchange_base64 = base64.b64encode(osmchange).decode('ascii')

	feature['properties']['@id'] = "node/" + str(osm_id)

	collection = {
		'type': 'FeatureCollection',
		'features': [
			feature
		],
		'cooperativeWork': {
			'meta': {
				'version': 2,
				'type': 2  # Change file type
			}
		},
		'file': {
			'type': 'xml',
			'format': 'osc',
			'encoding': 'base64',
			'content': osmchange_base64
		}
	}

	return collection



# Main program

if __name__ == '__main__':

	# Load geojson file with points

	if len(sys.argv) > 1:
		filename = sys.argv[1]
		if ".geojson" in filename:
			file = open(filename)
			osm_data = json.load(file)
			file.close()
		else:
			sys.exit("Only geojson files are supported\n")
	else:
		sys.exit("Please enter geojson file name\n")

	message ("Loaded %i elements fra '%s'\n" % (len(osm_data['features']), filename))

	# Extend geojson file for Maproulette collacboration challenge

	out_filename = filename.replace(".geojson", "") + "_maproulette.geojson"
	file = open(out_filename, "w")

	osm_id = -1000

	for feature in osm_data['features']:
		osm_id -= 1
		collection = convert_element(feature, osm_id)
		file.write(chr(30) + json.dumps(collection) + "\n")  # geojson line format

	file.close()

	message ("Saved in converted MapRoulette cooperative format to '%s'\n" % out_filename)
