#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:45
# @Author: Tang Chao
# @File: request.py
# @Software: PyCharm

class Request:
	def __init__(self, identity, pickup_node_id, delivery_node_id, require_capacity, vehicle_set):
		self.identity = identity
		self.pick_node_id = pickup_node_id
		self.delivery_node_id = delivery_node_id
		self.require_capacity = require_capacity
		self.vehicle_set: set = vehicle_set
	