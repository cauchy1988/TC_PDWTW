#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 23:04
# @Author: Tang Chao
# @File: vehicle.py
# @Software: PyCharm
from __future__ import annotations


class Vehicle:
	def __init__(self, identity: int, capacity: float, velocity: float, start_node_id: int, end_node_id: int):
		self.identity: int = identity
		self.capacity: float = capacity
		self.velocity: float = velocity
		self.start_node_id: int = start_node_id
		self.end_node_id: int = end_node_id
	
	def equals(self, other_vehicle: Vehicle) -> bool:
		return  self.capacity == other_vehicle.capacity and \
				self.velocity == other_vehicle.velocity and \
				self.start_node_id == other_vehicle.start_node_id and \
				self.end_node_id == other_vehicle.end_node_id
	