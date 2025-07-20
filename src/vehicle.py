#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:04
# @Author  : Tang Chao
# @File    : vehicle.py
# @Software: PyCharm

class Vehicle:
	def __init__(self, identity, capacity, velocity, start_node_id, end_node_id):
		self._identity = identity
		self._capacity = capacity
		self._velocity = velocity
		self._startNodeId = start_node_id
		self._endNodeId = end_node_id
		
	@property
	def identity(self):
		return self._identity
	
	@property
	def capacity(self):
		return self._capacity
	
	@property
	def velocity(self):
		return self._velocity
	
	@property
	def start_node_id(self):
		return self._startNodeId
	
	@property
	def end_node_id(self):
		return self._endNodeId
