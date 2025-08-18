package com.tc.pdwtw.model;

import com.tc.pdwtw.util.Parameters;
import java.util.*;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Meta class containing all problem data and configuration
 */
public class Meta {
    private Parameters parameters;
    private Map<Integer, Map<Integer, Double>> distances;
    private Map<Integer, Node> nodes;
    private Map<Integer, Request> requests;
    private Map<Integer, Vehicle> vehicles;
    private Map<Integer, Map<Integer, Map<Integer, Double>>> vehicleRunBetweenNodesTime;

    public Meta(Parameters parameters) {
        this.parameters = parameters;
        this.distances = new HashMap<>();
        this.nodes = new HashMap<>();
        this.requests = new HashMap<>();
        this.vehicles = new HashMap<>();
        this.vehicleRunBetweenNodesTime = new HashMap<>();
    }

    public Meta copy() {
        Meta newMeta = new Meta(this.parameters);
        
        // Deep copy distances
        for (Map.Entry<Integer, Map<Integer, Double>> entry : distances.entrySet()) {
            newMeta.distances.put(entry.getKey(), new HashMap<>(entry.getValue()));
        }
        
        // Deep copy nodes
        for (Map.Entry<Integer, Node> entry : nodes.entrySet()) {
            Node node = entry.getValue();
            newMeta.nodes.put(entry.getKey(), new Node(
                node.getNodeId(), node.getX(), node.getY(),
                node.getEarliestServiceTime(), node.getLatestServiceTime(),
                node.getServiceTime(), node.getLoad()
            ));
        }
        
        // Deep copy requests
        for (Map.Entry<Integer, Request> entry : requests.entrySet()) {
            Request req = entry.getValue();
            newMeta.requests.put(entry.getKey(), new Request(
                req.getIdentity(), req.getPickNodeId(), req.getDeliveryNodeId(),
                req.getRequireCapacity(), new HashSet<>(req.getVehicleSet())
            ));
        }
        
        // Deep copy vehicles
        for (Map.Entry<Integer, Vehicle> entry : vehicles.entrySet()) {
            Vehicle veh = entry.getValue();
            newMeta.vehicles.put(entry.getKey(), new Vehicle(
                veh.getIdentity(), veh.getCapacity(), veh.getVelocity(),
                veh.getStartNodeId(), veh.getEndNodeId()
            ));
        }
        
        // Deep copy vehicle run times
        for (Map.Entry<Integer, Map<Integer, Map<Integer, Double>>> vehEntry : vehicleRunBetweenNodesTime.entrySet()) {
            Map<Integer, Map<Integer, Double>> vehTimes = new HashMap<>();
            for (Map.Entry<Integer, Map<Integer, Double>> fromEntry : vehEntry.getValue().entrySet()) {
                vehTimes.put(fromEntry.getKey(), new HashMap<>(fromEntry.getValue()));
            }
            newMeta.vehicleRunBetweenNodesTime.put(vehEntry.getKey(), vehTimes);
        }
        
        return newMeta;
    }

    public int addOneSameVehicle(Integer newVehicleId) {
        if (vehicles.isEmpty()) {
            throw new RuntimeException("vehicles is empty!");
        }

        if (newVehicleId == null) {
            int maxVehicleId = Collections.max(vehicles.keySet());
            newVehicleId = maxVehicleId + 1;
        }

        if (vehicles.containsKey(newVehicleId)) {
            throw new IllegalArgumentException("Vehicle with ID " + newVehicleId + " already exists!");
        }

        Vehicle referenceVehicle = vehicles.values().iterator().next();
        
        int newVehicleStartNodeId = Collections.max(nodes.keySet()) + 1;
        int newVehicleEndNodeId = newVehicleStartNodeId + 1;

        Node randomDepotNode = nodes.get(referenceVehicle.getStartNodeId());
        nodes.put(newVehicleStartNodeId, new Node(
            newVehicleStartNodeId, randomDepotNode.getX(), randomDepotNode.getY(),
            randomDepotNode.getEarliestServiceTime(), randomDepotNode.getLatestServiceTime(),
            randomDepotNode.getServiceTime(), randomDepotNode.getLoad()
        ));
        nodes.put(newVehicleEndNodeId, new Node(
            newVehicleEndNodeId, randomDepotNode.getX(), randomDepotNode.getY(),
            randomDepotNode.getEarliestServiceTime(), randomDepotNode.getLatestServiceTime(),
            randomDepotNode.getServiceTime(), randomDepotNode.getLoad()
        ));

        vehicles.put(newVehicleId, new Vehicle(
            newVehicleId, referenceVehicle.getCapacity(), referenceVehicle.getVelocity(),
            newVehicleStartNodeId, newVehicleEndNodeId
        ));

        // Initialize vehicle run times
        vehicleRunBetweenNodesTime.put(newVehicleId, new HashMap<>());
        for (Integer fromNodeId : nodes.keySet()) {
            vehicleRunBetweenNodesTime.get(newVehicleId).put(fromNodeId, new HashMap<>());
            for (Integer toNodeId : nodes.keySet()) {
                if (fromNodeId.equals(toNodeId)) {
                    vehicleRunBetweenNodesTime.get(newVehicleId).get(fromNodeId).put(toNodeId, 0.0);
                } else {
                    double distance = distances.getOrDefault(fromNodeId, new HashMap<>()).getOrDefault(toNodeId, 0.0);
                    double travelTime = referenceVehicle.getVelocity() > 0 ? distance / referenceVehicle.getVelocity() : distance;
                    vehicleRunBetweenNodesTime.get(newVehicleId).get(fromNodeId).put(toNodeId, travelTime);
                }
            }
        }

        // Add vehicle to all requests
        for (Request request : requests.values()) {
            request.getVehicleSet().add(newVehicleId);
        }

        // Update distances
        int randomDepotNodeId = randomDepotNode.getNodeId();
        for (Map<Integer, Double> toNodeDict : distances.values()) {
            toNodeDict.put(newVehicleStartNodeId, toNodeDict.get(randomDepotNodeId));
            toNodeDict.put(newVehicleEndNodeId, toNodeDict.get(randomDepotNodeId));
        }
        
        distances.put(newVehicleStartNodeId, new HashMap<>(distances.get(randomDepotNodeId)));
        distances.get(newVehicleStartNodeId).put(newVehicleEndNodeId, 0.0);
        distances.put(newVehicleEndNodeId, new HashMap<>(distances.get(randomDepotNodeId)));
        distances.get(newVehicleEndNodeId).put(newVehicleStartNodeId, 0.0);

        // Update vehicle run times for all vehicles
        for (Map<Integer, Map<Integer, Double>> timeDict : vehicleRunBetweenNodesTime.values()) {
            for (Map<Integer, Double> toNodeDict : timeDict.values()) {
                toNodeDict.put(newVehicleStartNodeId, toNodeDict.get(randomDepotNodeId));
                toNodeDict.put(newVehicleEndNodeId, toNodeDict.get(randomDepotNodeId));
            }
            timeDict.put(newVehicleStartNodeId, new HashMap<>(timeDict.get(randomDepotNodeId)));
            timeDict.put(newVehicleEndNodeId, new HashMap<>(timeDict.get(randomDepotNodeId)));
            timeDict.get(newVehicleStartNodeId).put(newVehicleEndNodeId, 0.0);
            timeDict.get(newVehicleEndNodeId).put(newVehicleStartNodeId, 0.0);
        }

        return newVehicleId;
    }

    public boolean deleteVehicle(int deletedVehicleId) {
        if (!vehicles.containsKey(deletedVehicleId)) {
            return false;
        }

        if (vehicles.size() <= 1) {
            throw new RuntimeException("Cannot delete the last vehicle! At least one vehicle must remain.");
        }

        Vehicle deletedVehicle = vehicles.get(deletedVehicleId);
        int startDepotNodeId = deletedVehicle.getStartNodeId();
        int endDepotNodeId = deletedVehicle.getEndNodeId();

        // Check if nodes are shared (should not happen)
        boolean startNodeInUse = vehicles.values().stream()
            .filter(v -> v.getIdentity() != deletedVehicleId)
            .anyMatch(v -> v.getStartNodeId() == startDepotNodeId || v.getEndNodeId() == startDepotNodeId);
        boolean endNodeInUse = vehicles.values().stream()
            .filter(v -> v.getIdentity() != deletedVehicleId)
            .anyMatch(v -> v.getStartNodeId() == endDepotNodeId || v.getEndNodeId() == endDepotNodeId);

        if (startNodeInUse || endNodeInUse) {
            throw new RuntimeException("Vehicle " + deletedVehicleId + " has shared nodes with other vehicles");
        }

        // Delete vehicle
        vehicles.remove(deletedVehicleId);
        vehicleRunBetweenNodesTime.remove(deletedVehicleId);

        // Delete nodes
        nodes.remove(startDepotNodeId);
        nodes.remove(endDepotNodeId);

        // Update time dictionaries
        for (Map<Integer, Map<Integer, Double>> timeDict : vehicleRunBetweenNodesTime.values()) {
            for (Map<Integer, Double> toNodeDict : timeDict.values()) {
                toNodeDict.remove(startDepotNodeId);
                toNodeDict.remove(endDepotNodeId);
            }
            timeDict.remove(startDepotNodeId);
            timeDict.remove(endDepotNodeId);
        }

        // Remove vehicle from all requests
        for (Request request : requests.values()) {
            request.getVehicleSet().remove(deletedVehicleId);
        }

        // Update distances
        for (Map<Integer, Double> nodeDict : distances.values()) {
            nodeDict.remove(startDepotNodeId);
            nodeDict.remove(endDepotNodeId);
        }
        distances.remove(startDepotNodeId);
        distances.remove(endDepotNodeId);

        return true;
    }

    public Double getMaxDistance() {
        if (distances.isEmpty()) {
            return null;
        }
        return distances.values().stream()
            .flatMap(map -> map.values().stream())
            .max(Double::compareTo)
            .orElse(null);
    }

    public Integer maxVehicleId() {
        return vehicles.isEmpty() ? null : Collections.max(vehicles.keySet());
    }

    public int getVehicleCount() {
        return vehicles.size();
    }

    // Getters and Setters
    public Parameters getParameters() { return parameters; }
    public void setParameters(Parameters parameters) { this.parameters = parameters; }
    
    public Map<Integer, Map<Integer, Double>> getDistances() { return distances; }
    public void setDistances(Map<Integer, Map<Integer, Double>> distances) { this.distances = distances; }
    
    public Map<Integer, Node> getNodes() { return nodes; }
    public void setNodes(Map<Integer, Node> nodes) { this.nodes = nodes; }
    
    public Map<Integer, Request> getRequests() { return requests; }
    public void setRequests(Map<Integer, Request> requests) { this.requests = requests; }
    
    public Map<Integer, Vehicle> getVehicles() { return vehicles; }
    public void setVehicles(Map<Integer, Vehicle> vehicles) { this.vehicles = vehicles; }
    
    public Map<Integer, Map<Integer, Map<Integer, Double>>> getVehicleRunBetweenNodesTime() { return vehicleRunBetweenNodesTime; }
    public void setVehicleRunBetweenNodesTime(Map<Integer, Map<Integer, Map<Integer, Double>>> vehicleRunBetweenNodesTime) { 
        this.vehicleRunBetweenNodesTime = vehicleRunBetweenNodesTime; 
    }
}