#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:35
# @Author: Tang Chao
# @File: node.py
# @Software: PyCharm

class Node:
	def __init__(self, identity, x, y, earliest_service_time, latest_service_time, service_time, load):
		self.identity = identity
		self.x = x
		self.y = y
		self.latest_service_time = earliest_service_time
		self.latest_service_time = latest_service_time
		self.service_time = service_time
		self.load = load
		