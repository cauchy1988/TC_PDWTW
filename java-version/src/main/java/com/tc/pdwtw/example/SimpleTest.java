package com.tc.pdwtw.example;

import com.tc.pdwtw.model.*;
import com.tc.pdwtw.util.Parameters;
import java.util.*;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Simple test class to demonstrate basic functionality
 */
public class SimpleTest {
    
    public static void main(String[] args) {
        System.out.println("TC PDWTW Java Implementation");
        System.out.println("=============================");
        
        try {
            // Create parameters
            Parameters params = new Parameters();
            System.out.println("Created parameters with alpha: " + params.getAlpha());
            
            // Create meta object
            Meta meta = new Meta(params);
            System.out.println("Created Meta object");
            
            // Create some test nodes
            Node depot = new Node(0, 0.0, 0.0, 0.0, 1000.0, 0.0, 0.0);
            Node pickup = new Node(1, 10.0, 10.0, 0.0, 100.0, 5.0, 10.0);
            Node delivery = new Node(2, 20.0, 20.0, 0.0, 200.0, 5.0, -10.0);
            
            meta.getNodes().put(0, depot);
            meta.getNodes().put(1, pickup);
            meta.getNodes().put(2, delivery);
            System.out.println("Added " + meta.getNodes().size() + " nodes");
            
            // Create distances
            meta.getDistances().put(0, new HashMap<>());
            meta.getDistances().put(1, new HashMap<>());
            meta.getDistances().put(2, new HashMap<>());
            
            meta.getDistances().get(0).put(0, 0.0);
            meta.getDistances().get(0).put(1, 14.14);
            meta.getDistances().get(0).put(2, 28.28);
            meta.getDistances().get(1).put(0, 14.14);
            meta.getDistances().get(1).put(1, 0.0);
            meta.getDistances().get(1).put(2, 14.14);
            meta.getDistances().get(2).put(0, 28.28);
            meta.getDistances().get(2).put(1, 14.14);
            meta.getDistances().get(2).put(2, 0.0);
            System.out.println("Set up distance matrix");
            
            // Create vehicle
            Vehicle vehicle = new Vehicle(1, 50.0, 1.0, 0, 0);
            meta.getVehicles().put(1, vehicle);
            System.out.println("Added vehicle with capacity: " + vehicle.getCapacity());
            
            // Initialize vehicle run times
            meta.getVehicleRunBetweenNodesTime().put(1, new HashMap<>());
            for (int i = 0; i < 3; i++) {
                meta.getVehicleRunBetweenNodesTime().get(1).put(i, new HashMap<>());
                for (int j = 0; j < 3; j++) {
                    double distance = meta.getDistances().get(i).get(j);
                    meta.getVehicleRunBetweenNodesTime().get(1).get(i).put(j, distance / vehicle.getVelocity());
                }
            }
            
            // Create request
            Set<Integer> vehicleSet = new HashSet<>();
            vehicleSet.add(1);
            Request request = new Request(1, 1, 2, 10.0, vehicleSet);
            meta.getRequests().put(1, request);
            System.out.println("Added request from node " + request.getPickNodeId() + " to " + request.getDeliveryNodeId());
            
            // Create solution
            PDWTWSolution solution = new PDWTWSolution(meta);
            System.out.println("Created solution with " + solution.getRequestBank().size() + " unassigned requests");
            
            // Try to insert request
            boolean inserted = solution.insertOneRequestToAnyVehicleRouteOptimal(1);
            System.out.println("Request insertion " + (inserted ? "successful" : "failed"));
            
            if (inserted) {
                System.out.println("Objective cost: " + solution.getObjectiveCost());
                System.out.println("Distance cost: " + solution.getDistanceCost());
                System.out.println("Time cost: " + solution.getTimeCost());
                System.out.println("Unassigned requests: " + solution.getRequestBank().size());
            }
            
            System.out.println("Test completed successfully!");
            
        } catch (Exception e) {
            System.err.println("Error during test: " + e.getMessage());
            e.printStackTrace();
        }
    }
}