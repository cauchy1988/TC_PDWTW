package com.tc.pdwtw.benchmark;

import com.tc.pdwtw.model.*;
import com.tc.pdwtw.util.Parameters;
import java.io.*;
import java.util.*;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Reader for Li & Lim PDPTW benchmark data files
 */
public class LiLimBenchmarkReader extends BenchmarkReader {

    public static class LiLimProblemParameters {
        public final int vehicleCount;
        public final double vehicleCapacity;
        public final double vehicleSpeed;

        public LiLimProblemParameters(int vehicleCount, double vehicleCapacity, double vehicleSpeed) {
            this.vehicleCount = vehicleCount;
            this.vehicleCapacity = vehicleCapacity;
            this.vehicleSpeed = vehicleSpeed;
        }
    }

    public static class LiLimDepotNode {
        public final int nodeId;
        public final double xCoord;
        public final double yCoord;
        public final double demand;
        public final double earliestTime;
        public final double latestTime;
        public final double serviceTime;
        public final int pickupIndex;
        public final int deliveryIndex;

        public LiLimDepotNode(int nodeId, double xCoord, double yCoord, double demand,
                             double earliestTime, double latestTime, double serviceTime,
                             int pickupIndex, int deliveryIndex) {
            this.nodeId = nodeId;
            this.xCoord = xCoord;
            this.yCoord = yCoord;
            this.demand = demand;
            this.earliestTime = earliestTime;
            this.latestTime = latestTime;
            this.serviceTime = serviceTime;
            this.pickupIndex = pickupIndex;
            this.deliveryIndex = deliveryIndex;
        }
    }

    public static class LiLimCustomerNode {
        public final int nodeId;
        public final double xCoord;
        public final double yCoord;
        public final double demand;
        public final double earliestTime;
        public final double latestTime;
        public final double serviceTime;
        public final int pickupIndex;
        public final int deliveryIndex;

        public LiLimCustomerNode(int nodeId, double xCoord, double yCoord, double demand,
                                double earliestTime, double latestTime, double serviceTime,
                                int pickupIndex, int deliveryIndex) {
            this.nodeId = nodeId;
            this.xCoord = xCoord;
            this.yCoord = yCoord;
            this.demand = demand;
            this.earliestTime = earliestTime;
            this.latestTime = latestTime;
            this.serviceTime = serviceTime;
            this.pickupIndex = pickupIndex;
            this.deliveryIndex = deliveryIndex;
        }
    }

    private LiLimProblemParameters problemParams;
    private LiLimDepotNode depot;
    private Map<Integer, LiLimCustomerNode> nodes;

    public LiLimBenchmarkReader() {
        this.nodes = new HashMap<>();
    }

    public void readFile(String filePath) throws IOException {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new FileNotFoundException("Li & Lim benchmark file not found: " + filePath);
        }

        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        }

        if (lines.size() < 3) {
            throw new IllegalArgumentException("File must have at least 3 lines, got " + lines.size());
        }

        // Parse first line: problem parameters
        this.problemParams = parseProblemParameters(lines.get(0));

        // Parse second line: depot information
        this.depot = parseDepotLine(lines.get(1));

        // Parse remaining lines: customer nodes
        this.nodes = parseCustomerNodes(lines.subList(2, lines.size()));
    }

    @Override
    public Meta getMetaObj() {
        Meta newMetaObj = new Meta(new Parameters());

        // Add customer nodes
        for (Map.Entry<Integer, LiLimCustomerNode> entry : nodes.entrySet()) {
            LiLimCustomerNode customNode = entry.getValue();
            newMetaObj.getNodes().put(entry.getKey(), new Node(
                customNode.nodeId, customNode.xCoord, customNode.yCoord,
                customNode.earliestTime, customNode.latestTime,
                customNode.serviceTime, customNode.demand
            ));
        }

        int currentMaxNodeId = Collections.max(newMetaObj.getNodes().keySet());

        // Create depot nodes for each vehicle
        int currentNodeId = currentMaxNodeId + 1;
        for (int vehicleId = 1; vehicleId <= problemParams.vehicleCount; vehicleId++) {
            int startNodeId = currentNodeId;
            int endNodeId = currentNodeId + problemParams.vehicleCount;

            newMetaObj.getVehicles().put(vehicleId, new Vehicle(
                vehicleId, problemParams.vehicleCapacity, problemParams.vehicleSpeed,
                startNodeId, endNodeId
            ));

            // Start depot of the vehicle
            newMetaObj.getNodes().put(startNodeId, new Node(
                startNodeId, depot.xCoord, depot.yCoord,
                depot.earliestTime, depot.latestTime,
                depot.serviceTime, depot.demand
            ));

            // End depot of the vehicle
            newMetaObj.getNodes().put(endNodeId, new Node(
                endNodeId, depot.xCoord, depot.yCoord,
                depot.earliestTime, depot.latestTime,
                depot.serviceTime, depot.demand
            ));

            currentNodeId++;
        }

        // Initialize distances
        Set<Integer> allNodeIds = newMetaObj.getNodes().keySet();
        for (Integer nodeId : allNodeIds) {
            newMetaObj.getDistances().put(nodeId, new HashMap<>());
        }

        List<Integer> nodeIdList = new ArrayList<>(allNodeIds);
        for (int i = 0; i < nodeIdList.size(); i++) {
            Integer nodeId1 = nodeIdList.get(i);
            Node node1 = newMetaObj.getNodes().get(nodeId1);
            newMetaObj.getDistances().get(nodeId1).put(nodeId1, 0.0);

            for (int j = i + 1; j < nodeIdList.size(); j++) {
                Integer nodeId2 = nodeIdList.get(j);
                Node node2 = newMetaObj.getNodes().get(nodeId2);

                double dx = node2.getX() - node1.getX();
                double dy = node2.getY() - node1.getY();
                double distance = Math.sqrt(dx * dx + dy * dy);
                distance = Math.round(distance * 1000.0) / 1000.0; // Round to 3 decimal places

                newMetaObj.getDistances().get(nodeId1).put(nodeId2, distance);
                newMetaObj.getDistances().get(nodeId2).put(nodeId1, distance);
            }
        }

        // Initialize vehicle run times
        for (Integer vehicleId : newMetaObj.getVehicles().keySet()) {
            newMetaObj.getVehicleRunBetweenNodesTime().put(vehicleId, new HashMap<>());
            for (Integer nodeId1 : allNodeIds) {
                newMetaObj.getVehicleRunBetweenNodesTime().get(vehicleId).put(nodeId1, new HashMap<>());
                for (Integer nodeId2 : allNodeIds) {
                    double distance = newMetaObj.getDistances().get(nodeId1).get(nodeId2);
                    double travelTime = problemParams.vehicleSpeed > 0 ? distance / problemParams.vehicleSpeed : distance;
                    newMetaObj.getVehicleRunBetweenNodesTime().get(vehicleId).get(nodeId1).put(nodeId2, travelTime);
                }
            }
        }

        // Initialize requests
        Set<Integer> vehicleIds = new HashSet<>(newMetaObj.getVehicles().keySet());
        List<int[]> pickupDeliveryPairs = getPickupDeliveryPairs();

        int requestId = 1;
        for (int[] pair : pickupDeliveryPairs) {
            int pickupNodeId = pair[0];
            int deliveryNodeId = pair[1];

            LiLimCustomerNode pickupNode = nodes.get(pickupNodeId);
            double requireCapacity = pickupNode.demand;

            newMetaObj.getRequests().put(requestId, new Request(
                requestId, pickupNodeId, deliveryNodeId, requireCapacity, new HashSet<>(vehicleIds)
            ));
            requestId++;
        }

        return newMetaObj;
    }

    private static LiLimProblemParameters parseProblemParameters(String line) {
        try {
            String[] parts = line.trim().split("\t");
            if (parts.length != 3) {
                throw new IllegalArgumentException("First line must have 3 fields, got " + parts.length);
            }

            int vehicleCount = Integer.parseInt(parts[0]);
            double vehicleCapacity = Double.parseDouble(parts[1]);
            double vehicleSpeed = Double.parseDouble(parts[2]);

            return new LiLimProblemParameters(vehicleCount, vehicleCapacity, vehicleSpeed);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid problem parameters line: " + line.trim(), e);
        }
    }

    private static LiLimDepotNode parseDepotLine(String line) {
        try {
            String[] parts = line.trim().split("\t");
            if (parts.length != 9) {
                throw new IllegalArgumentException("Depot line must have 9 fields, got " + parts.length);
            }

            int nodeId = Integer.parseInt(parts[0]);
            if (nodeId != 0) {
                throw new IllegalArgumentException("Depot node_id must be 0, got " + nodeId);
            }

            return new LiLimDepotNode(
                Integer.parseInt(parts[0]),
                Double.parseDouble(parts[1]),
                Double.parseDouble(parts[2]),
                Double.parseDouble(parts[3]),
                Double.parseDouble(parts[4]),
                Double.parseDouble(parts[5]),
                Double.parseDouble(parts[6]),
                Integer.parseInt(parts[7]),
                Integer.parseInt(parts[8])
            );
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Invalid depot line: " + line.trim(), e);
        }
    }

    private static Map<Integer, LiLimCustomerNode> parseCustomerNodes(List<String> lines) {
        Map<Integer, LiLimCustomerNode> nodes = new HashMap<>();

        for (int lineNum = 0; lineNum < lines.size(); lineNum++) {
            String line = lines.get(lineNum).trim();
            if (line.isEmpty()) {
                continue;
            }

            try {
                String[] parts = line.split("\t");
                if (parts.length != 9) {
                    throw new IllegalArgumentException("Customer node line must have 9 fields, got " + parts.length);
                }

                int nodeId = Integer.parseInt(parts[0]);
                if (nodeId == 0) {
                    throw new IllegalArgumentException("Customer node line " + (lineNum + 3) + " has node_id 0, which should only be depot");
                }

                LiLimCustomerNode node = new LiLimCustomerNode(
                    Integer.parseInt(parts[0]),
                    Double.parseDouble(parts[1]),
                    Double.parseDouble(parts[2]),
                    Double.parseDouble(parts[3]),
                    Double.parseDouble(parts[4]),
                    Double.parseDouble(parts[5]),
                    Double.parseDouble(parts[6]),
                    Integer.parseInt(parts[7]),
                    Integer.parseInt(parts[8])
                );

                nodes.put(nodeId, node);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Invalid customer node line " + (lineNum + 3) + ": " + line, e);
            }
        }

        return nodes;
    }

    public List<int[]> getPickupDeliveryPairs() {
        List<int[]> pairs = new ArrayList<>();
        
        for (Map.Entry<Integer, LiLimCustomerNode> entry : nodes.entrySet()) {
            LiLimCustomerNode node = entry.getValue();
            if (node.demand > 0) { // Pickup node
                if (node.deliveryIndex != 0) {
                    pairs.add(new int[]{entry.getKey(), node.deliveryIndex});
                }
            }
        }
        
        return pairs;
    }

    public List<LiLimCustomerNode> getPickupNodes() {
        return nodes.values().stream()
            .filter(node -> node.demand > 0)
            .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }

    public List<LiLimCustomerNode> getDeliveryNodes() {
        return nodes.values().stream()
            .filter(node -> node.demand < 0)
            .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }

    public boolean validateData() {
        if (depot == null || depot.nodeId != 0) {
            return false;
        }

        List<LiLimCustomerNode> pickupNodes = getPickupNodes();
        List<LiLimCustomerNode> deliveryNodes = getDeliveryNodes();

        if (pickupNodes.size() != deliveryNodes.size()) {
            return false;
        }

        for (LiLimCustomerNode pickupNode : pickupNodes) {
            if (pickupNode.deliveryIndex == 0) {
                return false;
            }

            LiLimCustomerNode deliveryNode = nodes.get(pickupNode.deliveryIndex);
            if (deliveryNode == null) {
                return false;
            }

            if (Math.abs(pickupNode.demand) != Math.abs(deliveryNode.demand)) {
                return false;
            }
        }

        return true;
    }

    public void printSummary() {
        System.out.println("=== Li & Lim PDPTW Benchmark Data Summary ===");
        System.out.println("Problem Parameters:");
        System.out.println("  - Vehicle Count: " + problemParams.vehicleCount);
        System.out.println("  - Vehicle Capacity: " + problemParams.vehicleCapacity);
        System.out.println("  - Vehicle Speed: " + problemParams.vehicleSpeed);

        System.out.println("\nDepot Information:");
        System.out.println("  - Node ID: " + depot.nodeId);
        System.out.println("  - Location: (" + depot.xCoord + ", " + depot.yCoord + ")");
        System.out.println("  - Time Window: [" + depot.earliestTime + ", " + depot.latestTime + "]");

        System.out.println("\nCustomer Nodes:");
        System.out.println("  - Total Nodes: " + nodes.size());
        System.out.println("  - Pickup Nodes: " + getPickupNodes().size());
        System.out.println("  - Delivery Nodes: " + getDeliveryNodes().size());

        System.out.println("\nPickup-Delivery Pairs:");
        List<int[]> pairs = getPickupDeliveryPairs();
        for (int i = 0; i < Math.min(5, pairs.size()); i++) {
            int[] pair = pairs.get(i);
            int pickupId = pair[0];
            int deliveryId = pair[1];
            LiLimCustomerNode pickupNode = nodes.get(pickupId);
            LiLimCustomerNode deliveryNode = nodes.get(deliveryId);
            System.out.println("  - Node " + pickupId + " (pickup " + pickupNode.demand + 
                             ") -> Node " + deliveryId + " (delivery " + deliveryNode.demand + ")");
        }

        if (pairs.size() > 5) {
            System.out.println("  ... and " + (pairs.size() - 5) + " more pairs");
        }
    }
}