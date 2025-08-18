package com.tc.pdwtw.model;

import java.util.*;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Path class representing a vehicle's route through pickup and delivery nodes
 */
public class Path {
  public void setMetaObj(Meta metaObj) {
    this.metaObj = metaObj;
  }

  private Meta metaObj;
    private int vehicleId;
    private List<Integer> route;
    private List<Double> startServiceTimeLine;
    private List<Double> loadLine;
    private List<Double> distances;

    public static class PathError extends RuntimeException {
        public PathError(String message) {
            super(message);
        }
    }

    public static class InsertionResult {
        public final boolean success;
        public final double distanceDiff;
        public final double timeCostDiff;
        public final Path newPath;

        public InsertionResult(boolean success, double distanceDiff, double timeCostDiff, Path newPath) {
            this.success = success;
            this.distanceDiff = distanceDiff;
            this.timeCostDiff = timeCostDiff;
            this.newPath = newPath;
        }
    }

    public Path(int vehicleId, Meta metaObj, boolean needInit) {
        this.metaObj = metaObj;
        this.vehicleId = vehicleId;

        if (needInit) {
            if (!metaObj.getVehicles().containsKey(vehicleId)) {
                throw new PathError("Vehicle " + vehicleId + " not found in meta_obj");
            }

            Vehicle vehicle = metaObj.getVehicles().get(vehicleId);
            int startNodeId = vehicle.getStartNodeId();
            int endNodeId = vehicle.getEndNodeId();

            if (!metaObj.getNodes().containsKey(startNodeId) || !metaObj.getNodes().containsKey(endNodeId)) {
                throw new PathError("Vehicle " + vehicleId + " nodes not found: start=" + startNodeId + ", end=" + endNodeId);
            }

            this.route = new ArrayList<>(Arrays.asList(startNodeId, endNodeId));

            Node startNode = metaObj.getNodes().get(startNodeId);
            Node endNode = metaObj.getNodes().get(endNodeId);
            double earliestTime = startNode.getEarliestServiceTime();
            double arrivalTime = earliestTime + startNode.getServiceTime() + 
                metaObj.getVehicleRunBetweenNodesTime().get(vehicleId).get(startNodeId).get(endNodeId);
            double latestTime = Math.max(arrivalTime, endNode.getEarliestServiceTime());

            if (latestTime > endNode.getLatestServiceTime()) {
                throw new PathError("Time window violation: " + latestTime + " > " + endNode.getLatestServiceTime());
            }

            this.startServiceTimeLine = new ArrayList<>(Arrays.asList(earliestTime, latestTime));
            this.loadLine = new ArrayList<>(Arrays.asList(startNode.getLoad(), startNode.getLoad() + endNode.getLoad()));

            double endDistance = metaObj.getDistances().get(startNodeId).get(endNodeId);
            this.distances = new ArrayList<>(Arrays.asList(0.0, endDistance));
        }
    }

    public Path(int vehicleId, Meta metaObj) {
        this(vehicleId, metaObj, true);
    }

    public Path copy() {
        Path newPath = new Path(this.vehicleId, this.metaObj, false);
        newPath.metaObj = this.metaObj;
        newPath.vehicleId = this.vehicleId;
        newPath.route = new ArrayList<>(this.route);
        newPath.startServiceTimeLine = new ArrayList<>(this.startServiceTimeLine);
        newPath.loadLine = new ArrayList<>(this.loadLine);
        newPath.distances = new ArrayList<>(this.distances);
        return newPath;
    }

    public boolean isPathFree() {
        return route.size() <= 2;
    }

    public double getWholeTimeCost() {
        return startServiceTimeLine.get(startServiceTimeLine.size() - 1) - startServiceTimeLine.get(0);
    }

    public double getWholeDistanceCost() {
        return distances.isEmpty() ? 0.0 : distances.get(distances.size() - 1);
    }

    private boolean updateServiceTimesAfterInsertion(int startIdx) {
        for (int i = startIdx; i < startServiceTimeLine.size(); i++) {
            int prevNodeId = route.get(i - 1);
            int currentNodeId = route.get(i);
            
            double newStartTime = Math.max(
                startServiceTimeLine.get(i - 1) + 
                metaObj.getNodes().get(prevNodeId).getServiceTime() + 
                metaObj.getVehicleRunBetweenNodesTime().get(vehicleId).get(prevNodeId).get(currentNodeId),
                metaObj.getNodes().get(currentNodeId).getEarliestServiceTime()
            );

            if (newStartTime > metaObj.getNodes().get(currentNodeId).getLatestServiceTime()) {
                return false;
            }
            startServiceTimeLine.set(i, newStartTime);
        }
        return true;
    }

    private boolean updateLoadsAfterInsertion(int pickIdx, int deliveryIdx) {
        for (int i = pickIdx; i <= deliveryIdx; i++) {
            int currentNodeId = route.get(i);
            double newLoad = loadLine.get(i - 1) + metaObj.getNodes().get(currentNodeId).getLoad();
            if (newLoad > metaObj.getVehicles().get(vehicleId).getCapacity()) {
                return false;
            }
            loadLine.set(i, newLoad);
        }
        return true;
    }

    private void updateDistancesAfterInsertion(int startIdx) {
        for (int i = startIdx; i < distances.size(); i++) {
            int prevNodeId = route.get(i - 1);
            int currentNodeId = route.get(i);
            double currentDistance = distances.get(i - 1) + 
                metaObj.getDistances().get(prevNodeId).get(currentNodeId);
            distances.set(i, currentDistance);
        }
    }

    public InsertionResult tryToInsertRequest(int requestId, int pickInsertIdx, int deliveryInsertIdx) {
        if (pickInsertIdx >= deliveryInsertIdx) {
            return new InsertionResult(false, 0.0, 0.0, null);
        }

        Request request = metaObj.getRequests().get(requestId);
        int pickNodeId = request.getPickNodeId();
        int deliveryNodeId = request.getDeliveryNodeId();

        route.add(pickInsertIdx, pickNodeId);
        route.add(deliveryInsertIdx, deliveryNodeId);

        double prevWholeTimeCost = getWholeTimeCost();
        startServiceTimeLine.add(pickInsertIdx, 0.0);
        startServiceTimeLine.add(deliveryInsertIdx, 0.0);

        if (!updateServiceTimesAfterInsertion(pickInsertIdx)) {
            return new InsertionResult(false, 0.0, 0.0, null);
        }

        double timeCostDiff = getWholeTimeCost() - prevWholeTimeCost;

        loadLine.add(pickInsertIdx, 0.0);
        loadLine.add(deliveryInsertIdx, 0.0);

        if (!updateLoadsAfterInsertion(pickInsertIdx, deliveryInsertIdx)) {
            return new InsertionResult(false, 0.0, 0.0, null);
        }

        double prevDistance = distances.isEmpty() ? 0.0 : distances.get(distances.size() - 1);
        distances.add(pickInsertIdx, 0.0);
        distances.add(deliveryInsertIdx, 0.0);

        updateDistancesAfterInsertion(pickInsertIdx);

        double currentDistance = distances.isEmpty() ? 0.0 : distances.get(distances.size() - 1);
        double distanceDiff = currentDistance - prevDistance;

        return new InsertionResult(true, distanceDiff, timeCostDiff, this);
    }

    public InsertionResult tryToInsertRequestOptimal(int requestId) {
        Request request = metaObj.getRequests().get(requestId);
        if (!request.getVehicleSet().contains(vehicleId)) {
            return new InsertionResult(false, 0.0, 0.0, null);
        }

        int routeLen = route.size();
        InsertionResult bestResult = null;
        double minCost = Double.MAX_VALUE;
        double alpha = metaObj.getParameters().getAlpha();
        double beta = metaObj.getParameters().getBeta();
        for (int i = 1; i < routeLen; i++) {
            for (int j = i + 1; j <= routeLen; j++) {
                Path newPath = this.copy();
                InsertionResult result = newPath.tryToInsertRequest(requestId, i, j);
                if (result.success) {
                    double currentCost = alpha * result.distanceDiff + beta * result.timeCostDiff;
                    if (currentCost < minCost) {
                        minCost = currentCost;
                        bestResult = result;
                    }
                }
            }
        }

        return bestResult != null
            ? new InsertionResult(true, bestResult.distanceDiff, bestResult.timeCostDiff, bestResult.newPath)
            : new InsertionResult(false, 0.0, 0.0, null);
    }

    public double getNodeStartServiceTime(int nodeId) {
        int nodeIdx = route.indexOf(nodeId);
        if (nodeIdx == -1) {
            throw new PathError("Node " + nodeId + " not found in route");
        }
        return startServiceTimeLine.get(nodeIdx);
    }

    public static class RemovalResult {
        public final double distanceDiff;
        public final double timeCostDiff;

        public RemovalResult(double distanceDiff, double timeCostDiff) {
            this.distanceDiff = distanceDiff;
            this.timeCostDiff = timeCostDiff;
        }
    }

    public RemovalResult tryToRemoveRequest(int requestId) {
        Request request = metaObj.getRequests().get(requestId);
        if (!request.getVehicleSet().contains(vehicleId)) {
            throw new PathError("Vehicle " + vehicleId + " not in request " + requestId + " vehicle set");
        }

        int pickNodeId = request.getPickNodeId();
        int deliveryNodeId = request.getDeliveryNodeId();

        int pickNodeIdx = route.indexOf(pickNodeId);
        int deliveryNodeIdx = route.indexOf(deliveryNodeId);

        if (pickNodeIdx <= 0 || deliveryNodeIdx <= 0) {
            throw new PathError("Invalid node indices: pick=" + pickNodeIdx + ", delivery=" + deliveryNodeIdx);
        }

        // Remove nodes
        route.remove(pickNodeIdx);
        route.remove(deliveryNodeIdx - 1); // Adjust index after first removal

        // Update service times
        double prevWholeTimeCost = getWholeTimeCost();
        startServiceTimeLine.remove(pickNodeIdx);
        startServiceTimeLine.remove(deliveryNodeIdx - 1);

        if (!updateServiceTimesAfterRemoval(pickNodeIdx)) {
            throw new PathError("Time window violation after removal");
        }

        double timeCostDiff = prevWholeTimeCost - getWholeTimeCost();

        // Update loads
        loadLine.remove(pickNodeIdx);
        loadLine.remove(deliveryNodeIdx - 1);

        if (!updateLoadsAfterRemoval(pickNodeIdx, deliveryNodeIdx)) {
            throw new PathError("Capacity violation after removal");
        }

        // Update distances
        double prevDistance = distances.isEmpty() ? 0.0 : distances.get(distances.size() - 1);
        distances.remove(pickNodeIdx);
        distances.remove(deliveryNodeIdx - 1);

        updateDistancesAfterRemoval(pickNodeIdx);

        double currentDistance = distances.isEmpty() ? 0.0 : distances.get(distances.size() - 1);
        double distanceDiff = prevDistance - currentDistance;

        return new RemovalResult(distanceDiff, timeCostDiff);
    }

    private boolean updateServiceTimesAfterRemoval(int startIdx) {
        for (int i = startIdx; i < startServiceTimeLine.size(); i++) {
            int prevNodeId = route.get(i - 1);
            int currentNodeId = route.get(i);

            double newStartTime = Math.max(
                startServiceTimeLine.get(i - 1) + 
                metaObj.getNodes().get(prevNodeId).getServiceTime() + 
                metaObj.getVehicleRunBetweenNodesTime().get(vehicleId).get(prevNodeId).get(currentNodeId),
                metaObj.getNodes().get(currentNodeId).getEarliestServiceTime()
            );

            if (newStartTime > metaObj.getNodes().get(currentNodeId).getLatestServiceTime()) {
                return false;
            }
            startServiceTimeLine.set(i, newStartTime);
        }
        return true;
    }

    private boolean updateLoadsAfterRemoval(int pickIdx, int deliveryIdx) {
        // Only update loads between pickup and delivery if there are nodes in between
        if (pickIdx < deliveryIdx - 1) {
            for (int i = pickIdx; i < deliveryIdx - 1; i++) {
                int currentNodeId = route.get(i);
                double newLoad = loadLine.get(i - 1) + metaObj.getNodes().get(currentNodeId).getLoad();
                if (newLoad > metaObj.getVehicles().get(vehicleId).getCapacity()) {
                    return false;
                }
                loadLine.set(i, newLoad);
            }
        }
        return true;
    }

    private void updateDistancesAfterRemoval(int startIdx) {
        for (int i = startIdx; i < distances.size(); i++) {
            int prevNodeId = route.get(i - 1);
            int currentNodeId = route.get(i);
            double currentDistance = distances.get(i - 1) + 
                metaObj.getDistances().get(prevNodeId).get(currentNodeId);
            distances.set(i, currentDistance);
        }
    }

    // Getters
    public List<Integer> getRoute() { return new ArrayList<>(route); }
    public List<Double> getStartServiceTimeLine() { return new ArrayList<>(startServiceTimeLine); }
    public List<Double> getLoadLine() { return new ArrayList<>(loadLine); }
    public List<Double> getDistances() { return new ArrayList<>(distances); }
    public int getVehicleId() { return vehicleId; }
    public Meta getMetaObj() { return metaObj; }
}