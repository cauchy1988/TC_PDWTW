#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2024 cauchy1988

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Benchmark Data Reader for Li & Lim PDPTW Dataset

This module provides functionality to read Li and Lim's benchmark data files
and organize them into three main data structures:
1. Problem parameters (vehicle count, capacity, speed)
2. Depot information
3. Node information table
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import os


@dataclass
class LiLimProblemParameters:
    """Problem parameters from the first line of Li & Lim benchmark file"""
    vehicle_count: int
    vehicle_capacity: float
    vehicle_speed: float  # Note: unused in Li & Lim dataset


@dataclass
class LiLimDepotNode:
    """Depot node information from the second line of Li & Lim benchmark file"""
    node_id: int
    x_coord: float
    y_coord: float
    demand: float
    earliest_time: float
    latest_time: float
    service_time: float
    pickup_index: int
    delivery_index: int


@dataclass
class LiLimCustomerNode:
    """Customer node information from subsequent lines of Li & Lim benchmark file"""
    node_id: int
    x_coord: float
    y_coord: float
    demand: float
    earliest_time: float
    latest_time: float
    service_time: float
    pickup_index: int
    delivery_index: int


class LiLimBenchmarkReader:
    """Reader for Li & Lim PDPTW benchmark data files"""
    
    def __init__(self):
        self.problem_params: LiLimProblemParameters = None
        self.depot: LiLimDepotNode = None
        self.nodes: Dict[int, LiLimCustomerNode] = {}
        
    def read_file(self, file_path: str) -> Tuple[LiLimProblemParameters, LiLimDepotNode, Dict[int, LiLimCustomerNode]]:
        """
        Read a Li & Lim benchmark data file and return the three data structures
        
        Args:
            file_path: Path to the Li & Lim benchmark data file
            
        Returns:
            Tuple of (problem_params, depot, nodes)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Li & Lim benchmark file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if len(lines) < 3:
            raise ValueError(f"File must have at least 3 lines, got {len(lines)}")
            
        # Parse first line: problem parameters
        self.problem_params = self._parse_problem_parameters(lines[0])
        
        # Parse second line: depot information
        self.depot = self._parse_depot_line(lines[1])
        
        # Parse remaining lines: customer nodes
        self.nodes = self._parse_customer_nodes(lines[2:])
        
        return self.problem_params, self.depot, self.nodes
    
    def _parse_problem_parameters(self, line: str) -> LiLimProblemParameters:
        """Parse the first line containing problem parameters"""
        try:
            parts = line.strip().split('\t')
            if len(parts) != 3:
                raise ValueError(f"First line must have 3 fields, got {len(parts)}")
                
            vehicle_count = int(parts[0])
            vehicle_capacity = float(parts[1])
            vehicle_speed = float(parts[2])
            
            return LiLimProblemParameters(vehicle_count, vehicle_capacity, vehicle_speed)
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid problem parameters line: {line.strip()}") from e
    
    def _parse_depot_line(self, line: str) -> LiLimDepotNode:
        """Parse the second line containing depot information"""
        try:
            parts = line.strip().split('\t')
            if len(parts) != 9:
                raise ValueError(f"Depot line must have 9 fields, got {len(parts)}")
                
            node_id = int(parts[0])
            if node_id != 0:
                raise ValueError(f"Depot node_id must be 0, got {node_id}")
                
            return LiLimDepotNode(
                node_id=int(parts[0]),
                x_coord=float(parts[1]),
                y_coord=float(parts[2]),
                demand=float(parts[3]),
                earliest_time=float(parts[4]),
                latest_time=float(parts[5]),
                service_time=float(parts[6]),
                pickup_index=int(parts[7]),
                delivery_index=int(parts[8])
            )
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid depot line: {line.strip()}") from e
    
    def _parse_customer_nodes(self, lines: List[str]) -> Dict[int, LiLimCustomerNode]:
        """Parse the remaining lines containing customer node information"""
        nodes = {}
        
        for line_num, line in enumerate(lines, start=3):  # Start from line 3
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            try:
                parts = line.split('\t')
                if len(parts) != 9:
                    raise ValueError(f"Customer node line must have 9 fields, got {len(parts)}")
                    
                node_id = int(parts[0])
                if node_id == 0:
                    raise ValueError(f"Customer node line {line_num} has node_id 0, which should only be depot")
                    
                node = LiLimCustomerNode(
                    node_id=int(parts[0]),
                    x_coord=float(parts[1]),
                    y_coord=float(parts[2]),
                    demand=float(parts[3]),
                    earliest_time=float(parts[4]),
                    latest_time=float(parts[5]),
                    service_time=float(parts[6]),
                    pickup_index=int(parts[7]),
                    delivery_index=int(parts[8])
                )
                
                nodes[node_id] = node
                
            except (ValueError, IndexError) as e:
                raise ValueError(f"Invalid customer node line {line_num}: {line}") from e
        
        return nodes
    
    def get_pickup_delivery_pairs(self) -> List[Tuple[int, int]]:
        """
        Extract pickup-delivery pairs from the parsed Li & Lim data
        
        Returns:
            List of tuples (pickup_node_id, delivery_node_id)
        """
        pairs = []
        
        for node_id, node in self.nodes.items():
            if node.demand > 0:  # Pickup node
                if node.delivery_index != 0:
                    pairs.append((node_id, node.delivery_index))
        
        return pairs
    
    def get_pickup_nodes(self) -> List[LiLimCustomerNode]:
        """Get all pickup nodes (positive demand)"""
        return [node for node in self.nodes.values() if node.demand > 0]
    
    def get_delivery_nodes(self) -> List[LiLimCustomerNode]:
        """Get all delivery nodes (negative demand)"""
        return [node for node in self.nodes.values() if node.demand < 0]
    
    def validate_data(self) -> bool:
        """
        Validate the parsed Li & Lim data for consistency
        
        Returns:
            True if data is valid, False otherwise
        """
        # Check if depot exists and has correct node_id
        if self.depot is None or self.depot.node_id != 0:
            return False
            
        # Check if all pickup nodes have corresponding delivery nodes
        pickup_nodes = self.get_pickup_nodes()
        delivery_nodes = self.get_delivery_nodes()
        
        if len(pickup_nodes) != len(delivery_nodes):
            return False
            
        # Check if pickup and delivery demands match (absolute values)
        for pickup_node in pickup_nodes:
            if pickup_node.delivery_index == 0:
                return False
                
            delivery_node = self.nodes.get(pickup_node.delivery_index)
            if delivery_node is None:
                return False
                
            if abs(pickup_node.demand) != abs(delivery_node.demand):
                return False
                
        return True
    
    def print_summary(self):
        """Print a summary of the parsed Li & Lim data"""
        print("=== Li & Lim PDPTW Benchmark Data Summary ===")
        print(f"Problem Parameters:")
        print(f"  - Vehicle Count: {self.problem_params.vehicle_count}")
        print(f"  - Vehicle Capacity: {self.problem_params.vehicle_capacity}")
        print(f"  - Vehicle Speed: {self.problem_params.vehicle_speed}")
        
        print(f"\nDepot Information:")
        print(f"  - Node ID: {self.depot.node_id}")
        print(f"  - Location: ({self.depot.x_coord}, {self.depot.y_coord})")
        print(f"  - Time Window: [{self.depot.earliest_time}, {self.depot.latest_time}]")
        
        print(f"\nCustomer Nodes:")
        print(f"  - Total Nodes: {len(self.nodes)}")
        print(f"  - Pickup Nodes: {len(self.get_pickup_nodes())}")
        print(f"  - Delivery Nodes: {len(self.get_delivery_nodes())}")
        
        print(f"\nPickup-Delivery Pairs:")
        pairs = self.get_pickup_delivery_pairs()
        for pickup_id, delivery_id in pairs[:5]:  # Show first 5 pairs
            pickup_node = self.nodes[pickup_id]
            delivery_node = self.nodes[delivery_id]
            print(f"  - Node {pickup_id} (pickup {pickup_node.demand}) -> Node {delivery_id} (delivery {delivery_node.demand})")
        
        if len(pairs) > 5:
            print(f"  ... and {len(pairs) - 5} more pairs")


def read_lim_benchmark_file(file_path: str) -> Tuple[LiLimProblemParameters, LiLimDepotNode, Dict[int, LiLimCustomerNode]]:
    """
    Convenience function to read a Li & Lim benchmark file
    
    Args:
        file_path: Path to the Li & Lim benchmark data file
        
    Returns:
        Tuple of (problem_params, depot, nodes)
    """
    reader = LiLimBenchmarkReader()
    return reader.read_file(file_path)


# Example usage
if __name__ == "__main__":
    # Example: read LR1_2_1.txt
    try:
        reader = LiLimBenchmarkReader()
        reader.read_file("benchmark/LR1_2_1.txt")
        
        # Print summary
        reader.print_summary()
        
        # Validate data
        if reader.validate_data():
            print("\n✅ Li & Lim data validation passed!")
        else:
            print("\n❌ Li & Lim data validation failed!")
            
    except Exception as e:
        print(f"Error reading Li & Lim benchmark file: {e}")
