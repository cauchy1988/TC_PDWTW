package com.tc.pdwtw.algorithm;

import com.tc.pdwtw.model.*;
import java.util.*;
import java.util.function.Function;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Insertion operators for ALNS algorithm
 */
public class InsertionOperators {

    public static class InsertionError extends RuntimeException {
        public InsertionError(String message) {
            super(message);
        }
    }

    @FunctionalInterface
    public interface InsertionOperator {
        void insert(Meta metaObj, PDWTWSolution solution, int q, boolean insertUnlimited, Function<Double, Double> noiseFunc);
    }

    private static Map<Integer, Map<Integer, Double>> getRequestVehicleCost(
            Meta metaObj, PDWTWSolution solution, Function<Double, Double> noiseFunc) {
        
        if (metaObj == null) {
            throw new IllegalArgumentException("metaObj cannot be null");
        }
        if (solution == null) {
            throw new IllegalArgumentException("solution cannot be null");
        }

        Map<Integer, Map<Integer, Double>> requestVehicleCost = new HashMap<>();

        Set<Integer> vehicles = new HashSet<>(solution.getVehicleBank());
        vehicles.addAll(solution.getPaths().keySet());

        if (vehicles.size() < solution.getVehicleBank().size() + solution.getPaths().size()) {
            throw new IllegalArgumentException("Vehicle IDs must all be unique in solution's vehicle bank and paths!");
        }

        for (Integer requestId : solution.getRequestBank()) {
            requestVehicleCost.put(requestId, new HashMap<>());

            for (Integer vehicleId : vehicles) {
                double cost;
                boolean ok = false;
                
                try {
                    PDWTWSolution.InsertionCostResult result = solution.costIfInsertRequestToVehiclePath(requestId, vehicleId);
                    ok = result.success;
                    cost = result.success ? result.cost : metaObj.getParameters().getUnlimitedFloatBound();
                } catch (Exception e) {
                    cost = metaObj.getParameters().getUnlimitedFloatBound();
                }

                if (!ok) {
                    cost = metaObj.getParameters().getUnlimitedFloatBound();
                }

                if (ok && noiseFunc != null) {
                    cost = noiseFunc.apply(cost);
                }

                requestVehicleCost.get(requestId).put(vehicleId, cost);
            }
        }

        return requestVehicleCost;
    }

    private static Map<Integer, Map<Integer, Double>> updateRequestVehicleCost(
            Meta metaObj, int alreadyInsertedVehicleId,
            Map<Integer, Map<Integer, Double>> requestVehicleCost,
            PDWTWSolution solution, int alreadyInsertedRequestId,
            Function<Double, Double> noiseFunc) {

        if (!requestVehicleCost.containsKey(alreadyInsertedRequestId)) {
            throw new IllegalArgumentException("Request " + alreadyInsertedRequestId + " does not exist in cost matrix");
        }

        Map<Integer, Map<Integer, Double>> newRequestVehicleCost = new HashMap<>();
        for (Map.Entry<Integer, Map<Integer, Double>> entry : requestVehicleCost.entrySet()) {
            if (!entry.getKey().equals(alreadyInsertedRequestId)) {
                newRequestVehicleCost.put(entry.getKey(), new HashMap<>(entry.getValue()));
            }
        }

        for (Map.Entry<Integer, Map<Integer, Double>> entry : newRequestVehicleCost.entrySet()) {
            Integer requestId = entry.getKey();
            Map<Integer, Double> vehicleDict = entry.getValue();

            if (!vehicleDict.containsKey(alreadyInsertedVehicleId)) {
                throw new RuntimeException("Vehicle " + alreadyInsertedVehicleId + " not found in cost matrix for request " + requestId);
            }

            double cost;
            boolean ok = false;
            
            try {
                PDWTWSolution.InsertionCostResult result = solution.costIfInsertRequestToVehiclePath(requestId, alreadyInsertedVehicleId);
                ok = result.success;
                cost = result.success ? result.cost : metaObj.getParameters().getUnlimitedFloatBound();
            } catch (Exception e) {
                cost = metaObj.getParameters().getUnlimitedFloatBound();
            }

            if (!ok) {
                cost = metaObj.getParameters().getUnlimitedFloatBound();
            }

            if (ok && noiseFunc != null) {
                cost = noiseFunc.apply(cost);
            }

            vehicleDict.put(alreadyInsertedVehicleId, cost);
        }

        return newRequestVehicleCost;
    }

    private static class BestInsertion {
        public final Integer requestId;
        public final Integer vehicleId;
        public final double cost;

        public BestInsertion(Integer requestId, Integer vehicleId, double cost) {
            this.requestId = requestId;
            this.vehicleId = vehicleId;
            this.cost = cost;
        }
    }

    private static BestInsertion findBestInsertion(Map<Integer, Map<Integer, Double>> requestVehicleCost, double unlimitedFloat) {
        double minimumCost = Double.POSITIVE_INFINITY;
        Integer requestIdForInsertion = null;
        Integer vehicleIdForInsertion = null;

        for (Map.Entry<Integer, Map<Integer, Double>> reqEntry : requestVehicleCost.entrySet()) {
            for (Map.Entry<Integer, Double> vehEntry : reqEntry.getValue().entrySet()) {
                if (vehEntry.getValue() < minimumCost) {
                    minimumCost = vehEntry.getValue();
                    requestIdForInsertion = reqEntry.getKey();
                    vehicleIdForInsertion = vehEntry.getKey();
                }
            }
        }

        return new BestInsertion(requestIdForInsertion, vehicleIdForInsertion, minimumCost);
    }

    public static void basicGreedyInsertion(Meta metaObj, PDWTWSolution solution, int q, 
                                          boolean insertUnlimited, Function<Double, Double> noiseFunc) {
        System.out.println("start greedy insertion");

        if (q <= 0) {
            throw new IllegalArgumentException("q must be positive, got " + q);
        }
        if (metaObj == null) {
            throw new IllegalArgumentException("metaObj cannot be null");
        }
        if (solution == null) {
            throw new IllegalArgumentException("solution cannot be null");
        }

        int qq = Math.min(solution.getRequestBank().size(), q);

        System.out.println("start _get_request_vehicle_cost");
        Map<Integer, Map<Integer, Double>> requestVehicleCost = getRequestVehicleCost(metaObj, solution, noiseFunc);
        System.out.println("end _get_request_vehicle_cost");

        int iterationNum = 0;
        int maxIterations = qq * 2;

        while ((insertUnlimited || iterationNum < qq) && iterationNum < maxIterations) {
            if (requestVehicleCost.isEmpty() || solution.getRequestBank().isEmpty()) {
                break;
            }

            BestInsertion best = findBestInsertion(requestVehicleCost, metaObj.getParameters().getUnlimitedFloat());

            if (best.requestId == null || best.vehicleId == null || 
                best.cost > metaObj.getParameters().getUnlimitedFloat()) {
                break;
            }

            boolean ok = solution.insertOneRequestToOneVehicleRouteOptimal(best.requestId, best.vehicleId);

            if (!ok) {
                throw new InsertionError("Insertion failed for request " + best.requestId + " in vehicle " + best.vehicleId + "!");
            }

            requestVehicleCost = updateRequestVehicleCost(
                metaObj, best.vehicleId, requestVehicleCost, 
                solution, best.requestId, noiseFunc
            );

            iterationNum++;
        }

        System.out.println("end greedy insertion");
    }

    private static class RequestCostPair {
        public final Integer requestId;
        public final double regretCost;

        public RequestCostPair(Integer requestId, double regretCost) {
            this.requestId = requestId;
            this.regretCost = regretCost;
        }
    }

    private static List<RequestCostPair> calculateRegretCost(Map<Integer, List<VehicleCostPair>> requestVehicleList, int k) {
        List<RequestCostPair> requestKCostList = new ArrayList<>();

        for (Map.Entry<Integer, List<VehicleCostPair>> entry : requestVehicleList.entrySet()) {
            Integer requestId = entry.getKey();
            List<VehicleCostPair> vehicleCostList = entry.getValue();

            if (vehicleCostList.size() < k) {
                throw new IllegalArgumentException("Request " + requestId + " has fewer than " + k + " vehicle options");
            }

            double kCostSum = 0.0;
            double bestCost = vehicleCostList.get(0).cost;

            for (int i = 0; i < k; i++) {
                kCostSum += (vehicleCostList.get(i).cost - bestCost);
            }

            requestKCostList.add(new RequestCostPair(requestId, kCostSum));
        }

        requestKCostList.sort((a, b) -> Double.compare(b.regretCost, a.regretCost));
        return requestKCostList;
    }

    private static class VehicleCostPair {
        public final Integer vehicleId;
        public final double cost;

        public VehicleCostPair(Integer vehicleId, double cost) {
            this.vehicleId = vehicleId;
            this.cost = cost;
        }
    }

    public static InsertionOperator createRegretInsertion(int k) {
        final int LOWEST_K_VALUE = 2;

        if (k < LOWEST_K_VALUE) {
            throw new IllegalArgumentException("k must be at least " + LOWEST_K_VALUE + ", got " + k);
        }

        return (metaObj, solution, q, insertUnlimited, noiseFunc) -> {
            System.out.println("start " + k + " regret insertion");

            if (q <= 0) {
                throw new IllegalArgumentException("q must be positive, got " + q);
            }
            if (metaObj == null) {
                throw new IllegalArgumentException("metaObj cannot be null");
            }
            if (solution == null) {
                throw new IllegalArgumentException("solution cannot be null");
            }

            int totalVehicleNum = solution.getVehicleBank().size() + solution.getPaths().size();
            if (k > totalVehicleNum) {
                throw new RuntimeException("Regret number " + k + " is bigger than total vehicle number " + totalVehicleNum + "!");
            }

            int qq = Math.min(solution.getRequestBank().size(), q);
            Map<Integer, Map<Integer, Double>> requestVehicleCost = getRequestVehicleCost(metaObj, solution, noiseFunc);

            int iterationNum = 0;
            int maxIterations = qq * 2;

            while ((insertUnlimited || iterationNum < qq) && iterationNum < maxIterations) {
                if (requestVehicleCost.isEmpty() || solution.getRequestBank().isEmpty()) {
                    break;
                }

                Map<Integer, List<VehicleCostPair>> requestVehicleList = new HashMap<>();

                for (Map.Entry<Integer, Map<Integer, Double>> reqEntry : requestVehicleCost.entrySet()) {
                    Integer requestId = reqEntry.getKey();
                    Map<Integer, Double> costDict = reqEntry.getValue();

                    if (costDict.size() < k) {
                        throw new IllegalArgumentException("Request " + requestId + " has fewer than " + k + " vehicle options");
                    }

                    List<VehicleCostPair> vehicleCostList = new ArrayList<>();
                    for (Map.Entry<Integer, Double> vehEntry : costDict.entrySet()) {
                        vehicleCostList.add(new VehicleCostPair(vehEntry.getKey(), vehEntry.getValue()));
                    }
                    vehicleCostList.sort(Comparator.comparingDouble(pair -> pair.cost));
                    requestVehicleList.put(requestId, vehicleCostList);
                }

                List<RequestCostPair> requestKCostList = calculateRegretCost(requestVehicleList, k);

                int j = 0;
                while (j < requestKCostList.size()) {
                    Integer requestId = requestKCostList.get(j).requestId;
                    if (requestVehicleList.containsKey(requestId) && !requestVehicleList.get(requestId).isEmpty()) {
                        double bestCost = requestVehicleList.get(requestId).get(0).cost;
                        if (bestCost <= metaObj.getParameters().getUnlimitedFloat()) {
                            break;
                        }
                    }
                    j++;
                }

                if (j >= requestKCostList.size()) {
                    break;
                }

                Integer requestIdForInsertion = requestKCostList.get(j).requestId;
                Integer vehicleIdForInsertion = requestVehicleList.get(requestIdForInsertion).get(0).vehicleId;

                boolean ok = solution.insertOneRequestToOneVehicleRouteOptimal(requestIdForInsertion, vehicleIdForInsertion);

                if (!ok) {
                    throw new InsertionError("Insertion failed for request " + requestIdForInsertion + " in vehicle " + vehicleIdForInsertion + "!");
                }

                requestVehicleCost = updateRequestVehicleCost(
                    metaObj, vehicleIdForInsertion, requestVehicleCost, 
                    solution, requestIdForInsertion, noiseFunc
                );

                iterationNum++;
            }

            System.out.println("end " + k + " regret insertion");
        };
    }
}