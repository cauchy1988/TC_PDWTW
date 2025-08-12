#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:45
# @Author: Tang Chao
# @File: request.py
# @Software: PyCharm
from typing import Set

class Request:
	def __init__(self, identity: int, pickup_node_id: int, delivery_node_id: int, require_capacity: float, vehicle_set: Set[int]):
		self.identity: int = identity
		self.pick_node_id: int = pickup_node_id
		self.delivery_node_id: int = delivery_node_id
		self.require_capacity: float = require_capacity
		self.vehicle_set: Set[int] = vehicle_set
	