#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:35
# @Author: Tang Chao
# @File: node.py
# @Software: PyCharm

class Node:
	"""Represents a node with spatial and temporal service constraints.

	   Attributes:
	       identity: Unique identifier for the node.
	       x: X-coordinate of the node's location.
	       y: Y-coordinate of the node's location.
	       earliest_service_time: The earliest time service can begin at this node.
	       latest_service_time: The latest time service can begin at this node.
	       service_time: The duration required to service the node.
	       load: The load or demand associated with the node.
	"""
	def __init__(self, identity: int, x: float, y: float, earliest_service_time: float, latest_service_time: float, service_time: float, load: float) -> None:
		self.identity = identity
		self.x = x
		self.y = y
		self.earliest_service_time = earliest_service_time
		self.latest_service_time = latest_service_time
		self.service_time = service_time
		self.load = load
		