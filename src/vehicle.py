#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:04
# @Author: Tang Chao
# @File: vehicle.py
# @Software: PyCharm
from __future__ import annotations


class Vehicle:
	def __init__(self, identity, capacity, velocity, start_node_id, end_node_id):
		self._identity = identity
		self._capacity = capacity
		self._velocity = velocity
		self._startNodeId = start_node_id
		self._endNodeId = end_node_id
	
	def equals(self, other_vehicle: Vehicle) -> bool:
		return  self._capacity == other_vehicle._capacity and \
				self._velocity == other_vehicle._velocity and \
				self._startNodeId == other_vehicle._startNodeId and \
				self._endNodeId == other_vehicle._endNodeId
	
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
