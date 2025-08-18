package com.tc.pdwtw.algorithm;

import com.tc.pdwtw.model.*;
import java.util.*;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Two-stage algorithm for PDWTW with homogeneous fleet
 */
public class TwoStage {

    public static class TwoStageError extends RuntimeException {
        public TwoStageError(String message) {
            super(message);
        }
    }

    public static class AlnsResult {
        public final PDWTWSolution solution;
        public final int iterationCount;

        public AlnsResult(PDWTWSolution solution, int iterationCount) {
            this.solution = solution;
            this.iterationCount = iterationCount;
        }
    }

    /**
     * First stage: minimize the number of vehicles in a homogeneous fleet.
     * 
     * This stage works in two phases:
     * 1. Insert all requests by adding vehicles as needed
     * 2. Iteratively remove vehicles and try to reassign requests
     * 
     * @param oneSolution Initial solution to optimize
     * @return Optimized solution with minimal vehicle count
     * @throws TwoStageError If algorithm fails to converge or encounters errors
     */
    public static PDWTWSolution firstStageToLimitVehicleNumInHomogeneousFleet(PDWTWSolution oneSolution) {
        if (oneSolution == null) {
            throw new IllegalArgumentException("oneSolution cannot be null");
        }

        // Phase 1: Insert all requests by adding vehicles as needed
        List<Integer> requestsInBank = new ArrayList<>(oneSolution.getRequestBank());
        
        int aIterationNum = 0;
        int maxIterations = 1000; // Prevent infinite loops
        boolean newVehicleAddFlag = false;

        while (!requestsInBank.isEmpty() && aIterationNum < maxIterations) {
            aIterationNum++;

            Integer currentRequest = requestsInBank.remove(0);
            if (oneSolution.insertOneRequestToAnyVehicleRouteOptimal(currentRequest)) {
                newVehicleAddFlag = false;
                continue;
            } else {
                // Check if we're stuck in a loop
                if (newVehicleAddFlag) {
                    throw new TwoStageError("Failed to insert request " + currentRequest + 
                                          " even after adding new vehicle. Algorithm may be stuck.");
                }

                oneSolution.addOneSameVehicle(null);
                requestsInBank.add(currentRequest);
                newVehicleAddFlag = true;
            }
        }

        if (aIterationNum >= maxIterations) {
            throw new TwoStageError("First stage failed to converge after " + maxIterations + " iterations");
        }

        PDWTWSolution resultSolution = oneSolution.copyWithDeepCopiedMeta();
        
        System.out.println("vehicle num: " + oneSolution.getPaths().size());

        // Create a copy of vehicle_bank to avoid modification during iteration
        List<Integer> vehicleBankCopy = new ArrayList<>(oneSolution.getVehicleBank());
        for (Integer vehicleId : vehicleBankCopy) {
            oneSolution.deleteVehicleAndItsRoute(vehicleId);
        }

        // Phase 2: Iteratively remove vehicles and try to reassign requests
        int totalIterationNum = aIterationNum;
        int maxTotalIterations = oneSolution.getMetaObj().getParameters().getTheta();

        while (totalIterationNum <= maxTotalIterations) {
            // Get the vehicle with maximum ID to remove
            Integer maxVehicleId = oneSolution.maxVehicleId();
            if (maxVehicleId == null) {
                break;
            }

            System.out.println("loop num : " + totalIterationNum + ", vehicle num : " + oneSolution.getPaths().size());

            // Remove the vehicle and its route
            oneSolution.deleteVehicleAndItsRoute(maxVehicleId);

            // Temporarily modify parameters for ALNS
            int originalIterationNum = oneSolution.getMetaObj().getParameters().getIterationNum();
            oneSolution.getMetaObj().getParameters().setIterationNum(oneSolution.getMetaObj().getParameters().getTau());
            
            try {
                // Try to reassign requests using ALNS
                ALNS.AlnsResult alnsResult = ALNS.adaptiveLargeNeighbourhoodSearch(
                    oneSolution.getMetaObj(), oneSolution, true, true);
                
                if (alnsResult.bestSolution.getRequestBank().isEmpty()) {
                    // Successfully reassigned all requests
                    resultSolution = alnsResult.bestSolution.copyWithDeepCopiedMeta();
                } else {
                    // Failed to reassign all requests, stop here
                    break;
                }

                totalIterationNum += alnsResult.totalIterations;
            } catch (Exception e) {
                // Handle any errors during ALNS, including vehicle deletion errors
                System.out.println("Warning: ALNS failed during vehicle removal: " + e.getMessage());
                break;
            } finally {
                // Reset parameters to original values
                oneSolution.getMetaObj().getParameters().setIterationNum(originalIterationNum);
            }
        }

        // Reset parameters to original values
        resultSolution.getMetaObj().getParameters().reset();
        return resultSolution;
    }

    /**
     * Two-stage algorithm for solving PDWTW with homogeneous fleet.
     * 
     * Stage 1: Minimize the number of vehicles
     * Stage 2: Optimize the solution using ALNS
     * 
     * @param initialSolution Initial solution to optimize
     * @return Optimized solution
     * @throws TwoStageError If algorithm fails to converge
     */
    public static PDWTWSolution twoStageAlgorithmInHomogeneousFleet(PDWTWSolution initialSolution) {
        if (initialSolution == null) {
            throw new IllegalArgumentException("initialSolution cannot be null");
        }

        System.out.println("Starting two-stage algorithm");
        
        // Stage 1: Minimize vehicle count
        System.out.println("Stage 1: Minimizing vehicle count");
        PDWTWSolution stage1Solution = firstStageToLimitVehicleNumInHomogeneousFleet(initialSolution);
        
        System.out.println("Stage 1 completed. Vehicle count: " + stage1Solution.getPaths().size());
        
        // Stage 2: Optimize using ALNS
        System.out.println("Stage 2: Optimizing with ALNS");
        
        try {
            // Stage 2: Full ALNS optimization
            ALNS.AlnsResult finalResult = ALNS.adaptiveLargeNeighbourhoodSearch(
                stage1Solution.getMetaObj(), stage1Solution, false, false);
            System.out.println("Stage 2 completed. Final objective cost: " + finalResult.bestSolution.getObjectiveCost());
            return finalResult.bestSolution;
        } catch (Exception e) {
            System.out.println("Warning: Stage 2 optimization failed: " + e.getMessage());
            return stage1Solution;
        }
    }

}