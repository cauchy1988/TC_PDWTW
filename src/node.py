#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/18 22:35
# @Author  : Tang Chao
# @File    : node.py
# @Software: PyCharm

class Node:
	def __init__(self, identity, x, y, earliest_service_time, latest_service_time, service_time, load):
		self._identity = identity
		self._x = x
		self._y = y
		self._earliestServiceTime = earliest_service_time
		self._latestServiceTime = latest_service_time
		self._serviceTime = service_time
		self._load = load
		
	@property
	def identity(self):
		return self._identity
	
	@property
	def x(self):
		return self._x
	
	@property
	def y(self):
		return self._y
	
	@property
	def earliest_service_time(self):
		return self._earliestServiceTime
	
	@property
	def latest_service_time(self):
		return self._latestServiceTime
	
	@property
	def service_time(self):
		return self._serviceTime
	
	@property
	def load(self):
		return self._load
		