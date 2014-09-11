#!/usr/bin/env python

import json
import urllib2
from pprint import pprint
import time
import requests


class stackdriver_nodejs(object):

	def __init__(self, port):
		self.port = str(port)

		self.id = self.get_instance_id()

        self.key = 'Stackdriver key'

		self.send_metric(self.stackdriver_output(), self.key)

	def get_nodejs_data(self):
		try:
			url = "http://localhost:" +  self.port + "/status"
			return json.load(urllib2.urlopen(url))

		except urllib2.URLError,e:
			raise Exception("Unable to connect to server")

	def get_instance_id(self):
		id = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id')
		return id.read()

	def stackdriver_output(self):
		output_list = []
		stats = { 'cpu': 0,
			'mem': 0,
			'cpu_per_req': 0,
			'jiffy_per_req': 0,
			'rps': 0,
			'events': 0,
			'open_conns': 0,
			'open_requests': 0
		}

		data = self.get_nodejs_data()

		for key, value in stats.items():
			for worker in range( len(data['worker']) ):
				stats[key] += data['worker'][worker][key]
			output = {
					'name': 'nodejs_' + key,
					'value': stats[key],
					'collected_at': int(time.time()),
					'instance': self.id
			}

			output_list.append(output)

		return output_list

	def send_metric(self, data, key):
    		headers = {
      			'content-type': 'application/json',
      			'x-stackdriver-apikey': key
    		}

    		gateway_msg = {
      			'timestamp': int(time.time()),
      			'proto_version': 1,
      			'data': data,
    		}

    		resp = requests.post(
      			'https://custom-gateway.stackdriver.com/v1/custom',
      			data=json.dumps(gateway_msg),
      			headers=headers)

    		assert resp.ok, 'Failed to submit custom metric.'

stackdriver_nodejs(80)