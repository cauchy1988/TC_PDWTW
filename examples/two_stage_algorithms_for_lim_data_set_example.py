#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/15 11:30
# @Author  : Tang Chao
# @File    : two_stage_algorithms_for_lim_data_set_example.py
# @Software: PyCharm
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from solution import PDWTWSolution
from benchmark_reader_for_lim_dataset import LiLimBenchmarkReader
from two_stage import two_stage_algorithm_in_homogeneous_fleet

def main():
	reader = LiLimBenchmarkReader()
	reader.read_file("benchmark/LR1_2_1.txt")
	reader.print_summary()
	if reader.validate_data():
		print("\n✅ Li & Lim data validation passed!")
	else:
		print("\n❌ Li & Lim data validation failed!")
		exit(-1)
		
	new_meta_obj = reader.get_meta_obj()
	initial_solution = PDWTWSolution(new_meta_obj)
	final_solution = two_stage_algorithm_in_homogeneous_fleet(initial_solution)
	
	exit(0)

if __name__ == "__main__":
	main()
