#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:45
# @Author: Tang Chao
# @File: request.py
# @Software: PyCharm

class Request:
	def __init__(self, identity, pickup_node_id, delivery_node_id, require_capacity, vehicle_set):
		self._identity = identity
		self._pickNodeId = pickup_node_id
		self._deliveryNodeId = delivery_node_id
		self._requireCapacity = require_capacity
		self._vehicleSet: set = vehicle_set
	
	@property
	def identity(self):
		return self._identity
	
	@property
	def pick_node_id(self):
		return self._pickNodeId
	
	@property
	def delivery_node_id(self):
		return self._deliveryNodeId
	
	@property
	def require_capacity(self):
		return self._requireCapacity
	
	@property
	def vehicle_set(self):
		return self._vehicleSet
	