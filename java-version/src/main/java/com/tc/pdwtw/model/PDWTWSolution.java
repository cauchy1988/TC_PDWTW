package com.tc.pdwtw.model;

import java.util.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Solution class for Pickup and Delivery Problem with Time Windows (PDWTW)
 */
public class PDWTWSolution extends Solution {
    private Map<Integer, Path> paths;
    private Set<Integer> requestBank;
    private Map<Integer, Integer> requestIdToVehicleId;
    private Map<Integer, Integer> nodeIdToVehicleId;
    private Set<Integer> vehicleBank;
    
    private double distanceCost;
    private double timeCost;
    
    private String fingerPrint;
    private boolean fingerPrintDirty;

    public PDWTWSolution(Meta metaObj) {
        super(metaObj);
        this.paths = new HashMap<>();
        this.requestBank = new HashSet<>(metaObj.getRequests().keySet());
        this.requestIdToVehicleId = new HashMap<>();
        this.nodeIdToVehicleId = new HashMap<>();
        this.vehicleBank = new HashSet<>(metaObj.getVehicles().keySet());
        
        this.distanceCost = 0.0;
        this.timeCost = 0.0;
        this.fingerPrintDirty = true;
    }

    public String getFingerPrint() {
        if (fingerPrintDirty || fingerPrint == null) {
            fingerPrint = generateSolutionFingerPrint();
            fingerPrintDirty = false;
        }
        return fingerPrint;
    }

    private void markFingerPrintDirty() {
        fingerPrintDirty = true;
    }

    private String generateSolutionFingerPrint() {
        try {
            StringBuilder sb = new StringBuilder();
            List<Integer> sortedVehicleIds = new ArrayList<>(paths.keySet());
            Collections.sort(sortedVehicleIds);
            
            for (Integer vehicleId : sortedVehicleIds) {
                Path path = paths.get(vehicleId);
                sb.append("(").append(vehicleId).append(",").append(path.getRoute()).append(")");
            }
            
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(sb.toString().getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 algorithm not available", e);
        }
    }

    public int addOneSameVehicle(Integer oneVehicleId) {
        int newVehicleId = metaObj.addOneSameVehicle(oneVehicleId);
        vehicleBank.add(newVehicleId);
        return newVehicleId;
    }

    public void deleteVehicleAndItsRoute(int deleteVehicleId) {
        if (!paths.containsKey(deleteVehicleId) && !vehicleBank.contains(deleteVehicleId)) {
            throw new IllegalArgumentException("Vehicle " + deleteVehicleId + " not found in solution");
        }
        
        Set<Integer> deletedRequests = new HashSet<>();
        for (Map.Entry<Integer, Integer> entry : requestIdToVehicleId.entrySet()) {
            if (entry.getValue() == deleteVehicleId) {
                deletedRequests.add(entry.getKey());
            }
        }
        
        removeRequests(deletedRequests);
        
        // Assert that delete_vehicle_id is definitely deleted from paths after remove_requests
        if (paths.containsKey(deleteVehicleId)) {
            throw new IllegalStateException("Vehicle " + deleteVehicleId + " should have been removed from paths");
        }
        
        if (!vehicleBank.contains(deleteVehicleId)) {
            throw new IllegalStateException("Vehicle " + deleteVehicleId + " not in vehicle bank");
        }
        
        vehicleBank.remove(deleteVehicleId);
        metaObj.deleteVehicle(deleteVehicleId);
    }

    private void copyWithoutMetaObj(PDWTWSolution newObj) {
        newObj.requestBank = new HashSet<>(this.requestBank);
        newObj.requestIdToVehicleId = new HashMap<>(this.requestIdToVehicleId);
        newObj.nodeIdToVehicleId = new HashMap<>(this.nodeIdToVehicleId);
        newObj.vehicleBank = new HashSet<>(this.vehicleBank);

        newObj.distanceCost = this.distanceCost;
        newObj.timeCost = this.timeCost;
        newObj.fingerPrintDirty = true;
    }


    public PDWTWSolution copyWithDeepCopiedMeta() {
        Meta copiedMetaObj = metaObj.copy();
        PDWTWSolution newObj = new PDWTWSolution(copiedMetaObj);
        for (Map.Entry<Integer, Path> entry : paths.entrySet()) {
            newObj.paths.put(entry.getKey(), entry.getValue().copy());
            newObj.paths.get(entry.getKey()).setMetaObj(copiedMetaObj);
        }

        copyWithoutMetaObj(newObj);

        return newObj;
    }

    public PDWTWSolution copy() {
        PDWTWSolution newObj = new PDWTWSolution(this.metaObj);

        for (Map.Entry<Integer, Path> entry : paths.entrySet()) {
          newObj.paths.put(entry.getKey(), entry.getValue().copy());
        }

        copyWithoutMetaObj(newObj);

        return newObj;
    }

    public double costIfRemoveRequest(int requestId) {
        if (!requestIdToVehicleId.containsKey(requestId)) {
            throw new IllegalArgumentException("Request " + requestId + " not found in solution");
        }
        
        int vehicleId = requestIdToVehicleId.get(requestId);
        if (!paths.containsKey(vehicleId)) {
            throw new RuntimeException("Vehicle " + vehicleId + " not found in paths");
        }
        
        Path originalPath = paths.get(vehicleId);
        if (originalPath == null) {
            throw new RuntimeException("Path for vehicle " + vehicleId + " is null");
        }
        
        Path copiedPath = originalPath.copy();
        Path.RemovalResult result = copiedPath.tryToRemoveRequest(requestId);
        
        return metaObj.getParameters().getAlpha() * result.distanceDiff + 
               metaObj.getParameters().getBeta() * result.timeCostDiff;
    }

    public void removeRequests(Set<Integer> requestIdSet) {
        for (Integer requestId : requestIdSet) {
            if (!requestIdToVehicleId.containsKey(requestId)) {
                throw new IllegalArgumentException("Request " + requestId + " not found in solution");
            }
            
            int vehicleId = requestIdToVehicleId.get(requestId);
            if (!paths.containsKey(vehicleId)) {
                throw new RuntimeException("Vehicle " + vehicleId + " not found in paths");
            }
            
            Path pathObj = paths.get(vehicleId);
            Path.RemovalResult result = pathObj.tryToRemoveRequest(requestId);
            
            // Update Solution's inner data structure
            requestBank.add(requestId);
            requestIdToVehicleId.remove(requestId);
            
            Request requestObj = metaObj.getRequests().get(requestId);
            int pickNodeId = requestObj.getPickNodeId();
            int deliveryNodeId = requestObj.getDeliveryNodeId();
            nodeIdToVehicleId.remove(pickNodeId);
            nodeIdToVehicleId.remove(deliveryNodeId);
            
            if (pathObj.isPathFree()) {
                paths.remove(vehicleId);
                vehicleBank.add(vehicleId);
            }
            
            updateObjectiveCostAll();
            markFingerPrintDirty();
        }
    }

    public static class InsertionCostResult {
        public final boolean success;
        public final double cost;

        public InsertionCostResult(boolean success, double cost) {
            this.success = success;
            this.cost = cost;
        }
    }

    public InsertionCostResult costIfInsertRequestToVehiclePath(int requestId, int vehicleId) {
        if (!requestBank.contains(requestId)) {
            throw new IllegalArgumentException("Request " + requestId + " not in request bank");
        }

        if (!vehicleBank.contains(vehicleId) && !paths.containsKey(vehicleId)) {
            throw new IllegalArgumentException("Vehicle " + vehicleId + " not found in solution");
        }

        Request request = metaObj.getRequests().get(requestId);
        if (!request.getVehicleSet().contains(vehicleId)) {
            return new InsertionCostResult(false, 0.0);
        }

        Path thePath;
        if (paths.containsKey(vehicleId)) {
            thePath = paths.get(vehicleId).copy();
        } else {
            thePath = new Path(vehicleId, metaObj);
        }

        Path.InsertionResult result = thePath.tryToInsertRequestOptimal(requestId);

        if (!result.success) {
            return new InsertionCostResult(false, 0.0);
        }

        double cost = metaObj.getParameters().getAlpha() * result.distanceDiff + 
                     metaObj.getParameters().getBeta() * result.timeCostDiff;
        return new InsertionCostResult(true, cost);
    }

    public boolean insertOneRequestToOneVehicleRouteOptimal(int requestId, int vehicleId) {
        if (!requestBank.contains(requestId)) {
            throw new IllegalArgumentException("Request " + requestId + " not in request bank");
        }
        
        Request request = metaObj.getRequests().get(requestId);
        if (!request.getVehicleSet().contains(vehicleId)) {
            return false;
        }
        
        Path thePath;
        if (vehicleBank.contains(vehicleId)) {
            thePath = new Path(vehicleId, metaObj);
        } else {
            if (!paths.containsKey(vehicleId)) {
                throw new IllegalArgumentException("Vehicle " + vehicleId + " not found in paths");
            }
            thePath = paths.get(vehicleId);
        }
        
        Path.InsertionResult result = thePath.tryToInsertRequestOptimal(requestId);
        if (result.success) {
            requestBank.remove(requestId);
            requestIdToVehicleId.put(requestId, vehicleId);
            paths.put(vehicleId, result.newPath);
            
            nodeIdToVehicleId.put(request.getPickNodeId(), vehicleId);
            nodeIdToVehicleId.put(request.getDeliveryNodeId(), vehicleId);
            
            if (vehicleBank.contains(vehicleId)) {
                vehicleBank.remove(vehicleId);
            }
            
            updateObjectiveCostAll();
            markFingerPrintDirty();
        }
        
        return result.success;
    }

    public boolean insertOneRequestToAnyVehicleRouteOptimal(int requestId) {
        if (!requestBank.contains(requestId)) {
            throw new IllegalArgumentException("Request " + requestId + " not in request bank");
        }
        
        Request request = metaObj.getRequests().get(requestId);
        Set<Integer> availableVehicles = new HashSet<>(request.getVehicleSet());
        availableVehicles.retainAll(vehicleBank);
        availableVehicles.addAll(paths.keySet());
        availableVehicles.retainAll(request.getVehicleSet());
        
        for (Integer vehicleId : availableVehicles) {
            if (insertOneRequestToOneVehicleRouteOptimal(requestId, vehicleId)) {
                return true;
            }
        }
        
        return false;
    }

    public double getNodeStartServiceTimeInPath(int nodeId) {
        if (!nodeIdToVehicleId.containsKey(nodeId)) {
            throw new IllegalArgumentException("Node " + nodeId + " not found in solution");
        }
        
        int vehicleId = nodeIdToVehicleId.get(nodeId);
        if (!paths.containsKey(vehicleId)) {
            throw new RuntimeException("Vehicle " + vehicleId + " not found in paths");
        }
        
        Path path = paths.get(vehicleId);
        return path.getNodeStartServiceTime(nodeId);
    }

    private void updateObjectiveCostAll() {
        distanceCost = 0.0;
        timeCost = 0.0;
        for (Path path : paths.values()) {
            distanceCost += path.getWholeDistanceCost();
            timeCost += path.getWholeTimeCost();
        }
    }

    public Integer maxVehicleId() {
        if (paths.isEmpty() && vehicleBank.isEmpty()) {
            return null;
        }
        
        int pathsMax = paths.isEmpty() ? 0 : Collections.max(paths.keySet());
        int bankMax = vehicleBank.isEmpty() ? 0 : Collections.max(vehicleBank);
        return Math.max(pathsMax, bankMax);
    }

    public double getObjectiveCost() {
        return metaObj.getParameters().getAlpha() * distanceCost + 
               metaObj.getParameters().getBeta() * timeCost + 
               metaObj.getParameters().getGama() * requestBank.size();
    }

    public double getObjectiveCostWithoutRequestBank() {
        return metaObj.getParameters().getAlpha() * distanceCost + 
               metaObj.getParameters().getBeta() * timeCost;
    }

    // Getters
    public Map<Integer, Path> getPaths() { return new HashMap<>(paths); }
    public Set<Integer> getRequestBank() { return new HashSet<>(requestBank); }
    public Map<Integer, Integer> getRequestIdToVehicleId() { return new HashMap<>(requestIdToVehicleId); }
    public Map<Integer, Integer> getNodeIdToVehicleId() { return new HashMap<>(nodeIdToVehicleId); }
    public Set<Integer> getVehicleBank() { return new HashSet<>(vehicleBank); }
    public double getDistanceCost() { return distanceCost; }
    public double getTimeCost() { return timeCost; }
}