package com.tc.pdwtw.algorithm;

import com.tc.pdwtw.model.*;
import java.util.*;
import java.util.function.Function;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Removal operators for ALNS algorithm
 */
public class RemovalOperators {

    public static class InnerDictForNormalization {
        public Map<Integer, Map<Integer, Double>> distancePickDict = new HashMap<>();
        public Map<Integer, Map<Integer, Double>> distanceDeliveryDict = new HashMap<>();
        public Map<Integer, Map<Integer, Double>> startTimeDiffPickDict = new HashMap<>();
        public Map<Integer, Map<Integer, Double>> startTimeDiffDeliveryDict = new HashMap<>();
        public Map<Integer, Map<Integer, Double>> loadDiffDict = new HashMap<>();
        public Map<Integer, Map<Integer, Double>> vehicleSetDiffDict = new HashMap<>();

        public InnerDictForNormalization copy() {
            InnerDictForNormalization newObj = new InnerDictForNormalization();
            newObj.distancePickDict = copyNestedMap(this.distancePickDict);
            newObj.distanceDeliveryDict = copyNestedMap(this.distanceDeliveryDict);
            newObj.startTimeDiffPickDict = copyNestedMap(this.startTimeDiffPickDict);
            newObj.startTimeDiffDeliveryDict = copyNestedMap(this.startTimeDiffDeliveryDict);
            newObj.loadDiffDict = copyNestedMap(this.loadDiffDict);
            newObj.vehicleSetDiffDict = copyNestedMap(this.vehicleSetDiffDict);
            return newObj;
        }

        private Map<Integer, Map<Integer, Double>> copyNestedMap(Map<Integer, Map<Integer, Double>> original) {
            Map<Integer, Map<Integer, Double>> copy = new HashMap<>();
            for (Map.Entry<Integer, Map<Integer, Double>> entry : original.entrySet()) {
                copy.put(entry.getKey(), new HashMap<>(entry.getValue()));
            }
            return copy;
        }
    }

    private static Map<Integer, Map<Integer, Double>> normalizeDict(Map<Integer, Map<Integer, Double>> nestedDict, double epsilon) {
        List<Double> allValues = new ArrayList<>();
        for (Map<Integer, Double> innerDict : nestedDict.values()) {
            allValues.addAll(innerDict.values());
        }

        if (allValues.isEmpty()) {
            return nestedDict;
        }

        double minValue = Collections.min(allValues);
        double maxValue = Collections.max(allValues);

        Map<Integer, Map<Integer, Double>> normalizedDict = new HashMap<>();
        
        if (Math.abs(maxValue - minValue) < epsilon) {
            for (Map.Entry<Integer, Map<Integer, Double>> outerEntry : nestedDict.entrySet()) {
                Map<Integer, Double> normalizedInner = new HashMap<>();
                for (Integer innerKey : outerEntry.getValue().keySet()) {
                    normalizedInner.put(innerKey, 0.0);
                }
                normalizedDict.put(outerEntry.getKey(), normalizedInner);
            }
        } else {
            for (Map.Entry<Integer, Map<Integer, Double>> outerEntry : nestedDict.entrySet()) {
                Map<Integer, Double> normalizedInner = new HashMap<>();
                for (Map.Entry<Integer, Double> innerEntry : outerEntry.getValue().entrySet()) {
                    double normalizedValue = (innerEntry.getValue() - minValue) / (maxValue - minValue);
                    normalizedInner.put(innerEntry.getKey(), normalizedValue);
                }
                normalizedDict.put(outerEntry.getKey(), normalizedInner);
            }
        }

        return normalizedDict;
    }

    public static InnerDictForNormalization generateNormalizationDict(Meta metaObj, PDWTWSolution solution) {
        Map<Integer, Map<Integer, Double>> distancePickDict = new HashMap<>();
        Map<Integer, Map<Integer, Double>> distanceDeliveryDict = new HashMap<>();
        Map<Integer, Map<Integer, Double>> startTimeDiffPickDict = new HashMap<>();
        Map<Integer, Map<Integer, Double>> startTimeDiffDeliveryDict = new HashMap<>();
        Map<Integer, Map<Integer, Double>> loadDiffDict = new HashMap<>();
        Map<Integer, Map<Integer, Double>> vehicleSetDiff = new HashMap<>();

        List<Integer> requestIdList = new ArrayList<>(solution.getRequestIdToVehicleId().keySet());
        Collections.sort(requestIdList);

        Map<Integer, Map<String, Object>> requestData = new HashMap<>();
        for (Integer reqId : requestIdList) {
            Request req = metaObj.getRequests().get(reqId);
            int pickNode = req.getPickNodeId();
            int deliveryNode = req.getDeliveryNodeId();
            
            Map<String, Object> data = new HashMap<>();
            data.put("pickNode", pickNode);
            data.put("deliveryNode", deliveryNode);
            data.put("pickTime", solution.getNodeStartServiceTimeInPath(pickNode));
            data.put("deliveryTime", solution.getNodeStartServiceTimeInPath(deliveryNode));
            data.put("capacity", req.getRequireCapacity());
            data.put("vehicleSet", req.getVehicleSet());
            requestData.put(reqId, data);
        }

        for (int i = 0; i < requestIdList.size(); i++) {
            Integer reqI = requestIdList.get(i);
            Map<String, Object> dataI = requestData.get(reqI);

            distancePickDict.put(reqI, new HashMap<>());
            distanceDeliveryDict.put(reqI, new HashMap<>());
            startTimeDiffPickDict.put(reqI, new HashMap<>());
            startTimeDiffDeliveryDict.put(reqI, new HashMap<>());
            loadDiffDict.put(reqI, new HashMap<>());
            vehicleSetDiff.put(reqI, new HashMap<>());

            for (int j = i + 1; j < requestIdList.size(); j++) {
                Integer reqJ = requestIdList.get(j);
                Map<String, Object> dataJ = requestData.get(reqJ);

                int pickNodeI = (Integer) dataI.get("pickNode");
                int pickNodeJ = (Integer) dataJ.get("pickNode");
                int deliveryNodeI = (Integer) dataI.get("deliveryNode");
                int deliveryNodeJ = (Integer) dataJ.get("deliveryNode");

                distancePickDict.get(reqI).put(reqJ, metaObj.getDistances().get(pickNodeI).get(pickNodeJ));
                distanceDeliveryDict.get(reqI).put(reqJ, metaObj.getDistances().get(deliveryNodeI).get(deliveryNodeJ));

                double pickTimeI = (Double) dataI.get("pickTime");
                double pickTimeJ = (Double) dataJ.get("pickTime");
                double deliveryTimeI = (Double) dataI.get("deliveryTime");
                double deliveryTimeJ = (Double) dataJ.get("deliveryTime");

                startTimeDiffPickDict.get(reqI).put(reqJ, Math.abs(pickTimeI - pickTimeJ));
                startTimeDiffDeliveryDict.get(reqI).put(reqJ, Math.abs(deliveryTimeI - deliveryTimeJ));

                double capacityI = (Double) dataI.get("capacity");
                double capacityJ = (Double) dataJ.get("capacity");
                loadDiffDict.get(reqI).put(reqJ, Math.abs(capacityI - capacityJ));

                @SuppressWarnings("unchecked")
                Set<Integer> vehicleSetI = (Set<Integer>) dataI.get("vehicleSet");
                @SuppressWarnings("unchecked")
                Set<Integer> vehicleSetJ = (Set<Integer>) dataJ.get("vehicleSet");
                
                Set<Integer> intersection = new HashSet<>(vehicleSetI);
                intersection.retainAll(vehicleSetJ);
                int intersectionSize = intersection.size();
                int minSetSize = Math.min(vehicleSetI.size(), vehicleSetJ.size());
                vehicleSetDiff.get(reqI).put(reqJ, 1.0 - (double) intersectionSize / minSetSize);
            }
        }

        InnerDictForNormalization normObj = new InnerDictForNormalization();
        normObj.distancePickDict = normalizeDict(distancePickDict, 1e-6);
        normObj.distanceDeliveryDict = normalizeDict(distanceDeliveryDict, 1e-6);
        normObj.startTimeDiffPickDict = normalizeDict(startTimeDiffPickDict, 1e-6);
        normObj.startTimeDiffDeliveryDict = normalizeDict(startTimeDiffDeliveryDict, 1e-6);
        normObj.loadDiffDict = normalizeDict(loadDiffDict, 1e-6);
        normObj.vehicleSetDiffDict = vehicleSetDiff;

        return normObj;
    }

    private static Function<Integer, Double> createRelatednessFunction(Meta metaObj, int baseRequestId, InnerDictForNormalization normObj) {
        return anotherRequestId -> {
            int firstId = Math.min(baseRequestId, anotherRequestId);
            int secondId = Math.max(baseRequestId, anotherRequestId);

            double distanceScore = normObj.distancePickDict.get(firstId).get(secondId) + 
                                 normObj.distanceDeliveryDict.get(firstId).get(secondId);

            double timeScore = normObj.startTimeDiffPickDict.get(firstId).get(secondId) + 
                             normObj.startTimeDiffDeliveryDict.get(firstId).get(secondId);

            double loadScore = normObj.loadDiffDict.get(firstId).get(secondId);
            double vehicleScore = normObj.vehicleSetDiffDict.get(firstId).get(secondId);

            return metaObj.getParameters().getShawParam1() * distanceScore +
                   metaObj.getParameters().getShawParam2() * timeScore +
                   metaObj.getParameters().getShawParam3() * loadScore +
                   metaObj.getParameters().getShawParam4() * vehicleScore;
        };
    }

    public static void shawRemoval(Meta metaObj, PDWTWSolution solution, int q) {
        if (q <= 0) {
            throw new IllegalArgumentException("q must be positive, got " + q);
        }

        Set<Integer> solutionRequestSet = new HashSet<>(solution.getRequestIdToVehicleId().keySet());
        if (q > solutionRequestSet.size()) {
            throw new RuntimeException("Cannot remove " + q + " requests from solution with only " + solutionRequestSet.size() + " requests");
        }

        if (q == 0) {
            return;
        }

        Random random = new Random();
        List<Integer> requestList = new ArrayList<>(solutionRequestSet);
        int r = requestList.get(random.nextInt(requestList.size()));
        Set<Integer> bigD = new HashSet<>();
        bigD.add(r);

        InnerDictForNormalization normObj = generateNormalizationDict(metaObj, solution);

        while (bigD.size() < q) {
            if (bigD.isEmpty()) {
                throw new RuntimeException("bigD is empty, this should not happen");
            }

            List<Integer> bigDList = new ArrayList<>(bigD);
            r = bigDList.get(random.nextInt(bigDList.size()));

            Set<Integer> remainingRequests = new HashSet<>(solutionRequestSet);
            remainingRequests.removeAll(bigD);
            
            if (remainingRequests.isEmpty()) {
                break;
            }

            List<Integer> remainingList = new ArrayList<>(remainingRequests);
            Function<Integer, Double> relatednessFunc = createRelatednessFunction(metaObj, r, normObj);
            remainingList.sort(Comparator.comparing(relatednessFunc::apply));

            double y = random.nextDouble();
            int selectionIndex = (int) (Math.pow(y, metaObj.getParameters().getP()) * remainingList.size());
            selectionIndex = Math.min(selectionIndex, remainingList.size() - 1);

            Integer selectedRequest = remainingList.get(selectionIndex);
            bigD.add(selectedRequest);
        }

        solution.removeRequests(bigD);
    }

    public static void randomRemoval(Meta metaObj, PDWTWSolution solution, int q) {
        if (q <= 0) {
            throw new IllegalArgumentException("q must be positive, got " + q);
        }

        if (metaObj == null) {
            throw new IllegalArgumentException("metaObj cannot be null");
        }

        List<Integer> solutionRequestList = new ArrayList<>(solution.getRequestIdToVehicleId().keySet());
        if (q > solutionRequestList.size()) {
            throw new RuntimeException("Cannot remove " + q + " requests from solution with only " + solutionRequestList.size() + " requests");
        }

        if (q == 0) {
            return;
        }

        Random random = new Random();
        List<Integer> selectedRequests = new ArrayList<>();
        for (int i = 0; i < q; i++) {
            int randomIndex = random.nextInt(solutionRequestList.size());
            selectedRequests.add(solutionRequestList.remove(randomIndex));
        }

        solution.removeRequests(new HashSet<>(selectedRequests));
    }

    public static void worstRemoval(Meta metaObj, PDWTWSolution solution, int q) {
        if (q <= 0) {
            throw new IllegalArgumentException("q must be positive, got " + q);
        }

        if (metaObj == null) {
            throw new IllegalArgumentException("metaObj cannot be null");
        }

        Random random = new Random();
        int remainingQ = q;

        while (remainingQ > 0) {
            List<Integer> currentRequests = new ArrayList<>(solution.getRequestIdToVehicleId().keySet());

            if (currentRequests.isEmpty()) {
                break;
            }

            if (currentRequests.size() == 0) {
                throw new RuntimeException("No requests available for removal");
            }

            currentRequests.sort((a, b) -> Double.compare(
                solution.costIfRemoveRequest(b), 
                solution.costIfRemoveRequest(a)
            ));

            double y = random.nextDouble();
            int selectionIndex = (int) (Math.pow(y, metaObj.getParameters().getPWorst()) * currentRequests.size());
            selectionIndex = Math.min(selectionIndex, currentRequests.size() - 1);

            Integer selectedRequest = currentRequests.get(selectionIndex);
            Set<Integer> toRemove = new HashSet<>();
            toRemove.add(selectedRequest);
            solution.removeRequests(toRemove);
            remainingQ--;
        }
    }
}