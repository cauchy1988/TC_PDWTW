package com.tc.pdwtw.algorithm;

import com.tc.pdwtw.model.*;
import com.tc.pdwtw.util.Parameters;
import java.util.*;
import java.util.function.Function;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Adaptive Large Neighbourhood Search (ALNS) algorithm for PDWTW problems
 */
public class ALNS {

    private static final int ACCEPTED_SET_MAXLEN = 25000;

    public static class AlnsResult {
        public final PDWTWSolution bestSolution;
        public final int totalIterations;

        public AlnsResult(PDWTWSolution bestSolution, int totalIterations) {
            this.bestSolution = bestSolution;
            this.totalIterations = totalIterations;
        }
    }

    @FunctionalInterface
    public interface RemovalOperator {
        void remove(Meta metaObj, PDWTWSolution solution, int q);
    }

    private static Function<Double, Double> createObjectiveNoiseWrapper(Meta metaObj, boolean useNoise, double maxDistance) {
        return cost -> {
            if (useNoise) {
                Random random = new Random();
                double noise = metaObj.getParameters().getEta() * maxDistance;
                return Math.max(0.0, random.nextDouble() * 2 * noise - noise + cost);
            }
            return cost;
        };
    }

    private static class WeightedSelection<T> {
        public final T item;
        public final int index;

        public WeightedSelection(T item, int index) {
            this.item = item;
            this.index = index;
        }
    }

    private static <T> WeightedSelection<T> selectFunctionWithWeight(List<T> functions, List<Double> weights) {
        if (functions.size() != weights.size()) {
            throw new IllegalArgumentException("weights must have same length as functions!");
        }

        Random random = new Random();
        
        // Handle case where all weights are zero or negative
        boolean allWeightsZero = weights.stream().allMatch(w -> w <= 0);
        if (allWeightsZero) {
            int selectedIndex = random.nextInt(functions.size());
            return new WeightedSelection<>(functions.get(selectedIndex), selectedIndex);
        }

        // Ensure all weights are non-negative
        List<Double> positiveWeights = new ArrayList<>();
        for (double w : weights) {
            positiveWeights.add(Math.max(0.0, w));
        }

        // Calculate cumulative weights
        double totalWeight = positiveWeights.stream().mapToDouble(Double::doubleValue).sum();
        double randomValue = random.nextDouble() * totalWeight;
        
        double cumulativeWeight = 0.0;
        for (int i = 0; i < functions.size(); i++) {
            cumulativeWeight += positiveWeights.get(i);
            if (randomValue <= cumulativeWeight) {
                return new WeightedSelection<>(functions.get(i), i);
            }
        }
        
        // Fallback to last element
        return new WeightedSelection<>(functions.get(functions.size() - 1), functions.size() - 1);
    }

    private static double computeInitialTemperature(double z0, double w, double p) {
        if (z0 <= 0.0) {
            throw new IllegalArgumentException("initial cost z0 should be positive z0=" + z0);
        }
        if (p <= 0 || p >= 1) {
            throw new IllegalArgumentException("receptive ratio p should be in the range (0,1)");
        }
        double delta = w * z0;
        return -delta / Math.log(p);
    }

    private static void assertLenEqual(List<Double> wList, List<Double> rewardList, List<Integer> thetaList) {
        if (wList.size() != rewardList.size() || thetaList.size() != wList.size()) {
            throw new IllegalArgumentException("Lists must have equal length");
        }
    }

    /**
     * Adaptive Large Neighbourhood Search (ALNS) algorithm for PDWTW problems.
     * 
     * This function implements the ALNS metaheuristic which iteratively improves
     * a solution by destroying and repairing it using various operators. The algorithm
     * adaptively adjusts operator weights based on their performance and uses
     * simulated annealing for acceptance decisions.
     * 
     * @param metaObj Meta object containing problem instance and parameters
     * @param initialSolution Starting solution to improve
     * @param insertUnlimited Whether to allow unlimited insertions
     * @param stopIfAllRequestsCoped Stop iteration if all requests are assigned
     * @return Best solution found during the search and iteration count
     */
    public static AlnsResult adaptiveLargeNeighbourhoodSearch(Meta metaObj, PDWTWSolution initialSolution, 
                                                            boolean insertUnlimited, boolean stopIfAllRequestsCoped) {
        // Input validation
        if (metaObj == null) {
            throw new IllegalArgumentException("metaObj cannot be null");
        }
        if (initialSolution == null) {
            throw new IllegalArgumentException("initialSolution cannot be null");
        }

        // Validate algorithm parameters
        Parameters params = metaObj.getParameters();
        if (params.getIterationNum() <= 0) {
            throw new IllegalArgumentException("iteration_num must be positive");
        }
        if (params.getRemoveLowerBound() < 0) {
            throw new IllegalArgumentException("remove_lower_bound must be non-negative");
        }
        if (params.getRemoveUpperBound() <= 0) {
            throw new IllegalArgumentException("remove_upper_bound must be positive");
        }
        if (params.getEpsilon() <= 0 || params.getEpsilon() > 1) {
            throw new IllegalArgumentException("epsilon must be in (0, 1]");
        }

        // Determine removal bounds based on problem size and parameters
        int requestsNum = metaObj.getRequests().size();
        int qUpperBound = Math.min(params.getRemoveUpperBound(), (int)(params.getEpsilon() * requestsNum));
        int qLowerBound = params.getRemoveLowerBound();

        // Validate removal bounds
        if (qUpperBound < qLowerBound) {
            throw new IllegalArgumentException("q_upper_bound (" + qUpperBound + ") must be >= q_lower_bound (" + qLowerBound + ")");
        }
        if (qLowerBound < 1) {
            throw new IllegalArgumentException("q_lower_bound must be at least 1");
        }

        // Initialize removal operators with equal weights
        List<Double> wRemoval = new ArrayList<>(Arrays.asList(
            (double)params.getInitialWeight(), 
            (double)params.getInitialWeight(), 
            (double)params.getInitialWeight()
        ));
        List<RemovalOperator> removalFunctionList = Arrays.asList(
            RemovalOperators::shawRemoval,
            RemovalOperators::randomRemoval,
            RemovalOperators::worstRemoval
        );
        List<Double> removalRewards = new ArrayList<>(Arrays.asList(0.0, 0.0, 0.0));
        List<Integer> removalTheta = new ArrayList<>(Arrays.asList(0, 0, 0));

        // Initialize insertion operators
        int m = initialSolution.getPaths().size() + initialSolution.getVehicleBank().size();
        List<Double> wInsertion = new ArrayList<>(Arrays.asList(
            (double)params.getInitialWeight(),
            (double)params.getInitialWeight(),
            (double)params.getInitialWeight(),
            (double)params.getInitialWeight(),
            (double)params.getInitialWeight()
        ));
        List<InsertionOperators.InsertionOperator> insertionFunctionList = Arrays.asList(
            InsertionOperators::basicGreedyInsertion,
            InsertionOperators.createRegretInsertion(2),
            InsertionOperators.createRegretInsertion(3),
            InsertionOperators.createRegretInsertion(4),
            InsertionOperators.createRegretInsertion(m)
        );
        List<Double> insertionRewards = new ArrayList<>(Arrays.asList(0.0, 0.0, 0.0, 0.0, 0.0));
        List<Integer> insertionTheta = new ArrayList<>(Arrays.asList(0, 0, 0, 0, 0));

        // Initialize noise operators
        List<Double> wNoise = new ArrayList<>(Arrays.asList((double)params.getInitialWeight(), (double)params.getInitialWeight()));
        List<Double> noiseRewards = new ArrayList<>(Arrays.asList(0.0, 0.0));
        List<Integer> noiseTheta = new ArrayList<>(Arrays.asList(0, 0));
        Double maxDistance = metaObj.getMaxDistance();
        if (maxDistance == null) maxDistance = 1000.0; // Default value
        
        List<Function<Double, Double>> noiseFunctionList = Arrays.asList(
            createObjectiveNoiseWrapper(metaObj, false, maxDistance),
            createObjectiveNoiseWrapper(metaObj, true, maxDistance)
        );

        // Initialize solution tracking
        PDWTWSolution sBest = initialSolution.copy();  // Best solution found so far
        PDWTWSolution s = initialSolution.copy();      // Current solution

        // Initialize simulated annealing temperature
        double tStart = computeInitialTemperature(
            initialSolution.getObjectiveCostWithoutRequestBank(), 
            params.getW(), 
            params.getAnnealingP()
        );
        double tCurrent = tStart;

        Set<String> acceptedSolutionSet = new HashSet<>();  // Track accepted solution fingerprints

        // Main ALNS loop
        System.out.println("start alns loop, total iteration_num : " + params.getIterationNum());
        Random random = new Random();
        int totalIterationNum = 0;
        
        while (totalIterationNum < params.getIterationNum()) {
            System.out.println("alns loop index : " + totalIterationNum);
            if (!stopIfAllRequestsCoped) {
                System.out.println("current best distance : " + sBest.getDistanceCost() + 
                                 ", request bank size : " + sBest.getRequestBank().size());
            }

            // Randomly select number of requests to remove
            int q = random.nextInt(qUpperBound - qLowerBound + 1) + qLowerBound;

            // Select operators using adaptive weights
            WeightedSelection<RemovalOperator> removeSelection = selectFunctionWithWeight(removalFunctionList, wRemoval);
            WeightedSelection<InsertionOperators.InsertionOperator> insertSelection = selectFunctionWithWeight(insertionFunctionList, wInsertion);
            WeightedSelection<Function<Double, Double>> noiseSelection = selectFunctionWithWeight(noiseFunctionList, wNoise);

            // Track operator usage
            removalTheta.set(removeSelection.index, removalTheta.get(removeSelection.index) + 1);
            insertionTheta.set(insertSelection.index, insertionTheta.get(insertSelection.index) + 1);
            noiseTheta.set(noiseSelection.index, noiseTheta.get(noiseSelection.index) + 1);

            // Apply destroy and repair operations
            PDWTWSolution sP = s.copy();  // Create candidate solution
            removeSelection.item.remove(metaObj, sP, q);  // Destroy: remove q requests
            insertSelection.item.insert(metaObj, sP, q, insertUnlimited, noiseSelection.item);  // Repair: reinsert requests

            // Skip if this solution configuration was already explored
            String fingerPrint = sP.getFingerPrint();
            if (acceptedSolutionSet.contains(fingerPrint)) {
                totalIterationNum++;
                continue;
            }

            // Pre-calculate objective cost and determine acceptance
            double sPCost = sP.getObjectiveCost();
            double originalCost = s.getObjectiveCost();

            // Check if new best solution found
            boolean isNewBest = false;
            List<Integer> rewardAdds = params.getRewardAdds();
            if (sPCost < sBest.getObjectiveCost()) {
                isNewBest = true;
                // Reward operators for finding new best solution
                removalRewards.set(removeSelection.index, removalRewards.get(removeSelection.index) + rewardAdds.get(0));
                insertionRewards.set(insertSelection.index, insertionRewards.get(insertSelection.index) + rewardAdds.get(0));
                noiseRewards.set(noiseSelection.index, noiseRewards.get(noiseSelection.index) + rewardAdds.get(0));
            }

            // Solution acceptance logic (simulated annealing)
            boolean isAccepted = false;
            if (sPCost <= originalCost) {
                // Accept improving solutions
                isAccepted = true;
                if (!isNewBest) {
                    // Reward for improving current solution (but not global best)
                    removalRewards.set(removeSelection.index, removalRewards.get(removeSelection.index) + rewardAdds.get(1));
                    insertionRewards.set(insertSelection.index, insertionRewards.get(insertSelection.index) + rewardAdds.get(1));
                    noiseRewards.set(noiseSelection.index, noiseRewards.get(noiseSelection.index) + rewardAdds.get(1));
                }
            } else {
                // Consider accepting worse solutions based on temperature
                double deltaObjectiveCost = sPCost - originalCost;
                double acceptRatio = Math.exp(-deltaObjectiveCost / tCurrent);
                double acceptRandom = random.nextDouble();
                if (acceptRandom <= acceptRatio) {
                    // Accept worse solution with probability based on temperature
                    isAccepted = true;
                    // Reward for diversification
                    removalRewards.set(removeSelection.index, removalRewards.get(removeSelection.index) + rewardAdds.get(2));
                    insertionRewards.set(insertSelection.index, insertionRewards.get(insertSelection.index) + rewardAdds.get(2));
                    noiseRewards.set(noiseSelection.index, noiseRewards.get(noiseSelection.index) + rewardAdds.get(2));
                }
            }

            // Only copy when necessary
            if (isNewBest) {
                sBest = sP.copy();  // Copy only when new best found
            }

            if (isAccepted) {
                s = sP;  // Transfer ownership instead of copy
                acceptedSolutionSet.add(fingerPrint);
                // Control accepted_solution_set maximum capacity to avoid memory overflow
                if (acceptedSolutionSet.size() > ACCEPTED_SET_MAXLEN) {
                    acceptedSolutionSet.clear(); // Simple approach - clear when too large
                }
            }

            // Adaptive weight update at segment boundaries
            if ((totalIterationNum + 1) % params.getSegmentNum() == 0) {
                double r = params.getR();
                double oneMinusR = 1 - r;

                // Update removal operator weights based on performance
                for (int i = 0; i < wRemoval.size(); i++) {
                    if (removalTheta.get(i) > 0) {
                        double newWeight = oneMinusR * wRemoval.get(i) + r * (removalRewards.get(i) / removalTheta.get(i));
                        wRemoval.set(i, Math.max(1e-8, newWeight));
                    } else {
                        wRemoval.set(i, Math.max(1e-8, wRemoval.get(i)));
                    }
                }

                // Update insertion operator weights based on performance
                for (int i = 0; i < wInsertion.size(); i++) {
                    if (insertionTheta.get(i) > 0) {
                        double newWeight = oneMinusR * wInsertion.get(i) + r * (insertionRewards.get(i) / insertionTheta.get(i));
                        wInsertion.set(i, Math.max(1e-8, newWeight));
                    } else {
                        wInsertion.set(i, Math.max(1e-8, wInsertion.get(i)));
                    }
                }

                // Update noise operator weights based on performance
                for (int i = 0; i < wNoise.size(); i++) {
                    if (noiseTheta.get(i) > 0) {
                        double newWeight = oneMinusR * wNoise.get(i) + r * (noiseRewards.get(i) / noiseTheta.get(i));
                        wNoise.set(i, Math.max(1e-8, newWeight));
                    } else {
                        wNoise.set(i, Math.max(1e-8, wNoise.get(i)));
                    }
                }

                // Reset statistics for next segment
                Collections.fill(removalRewards, 0.0);
                Collections.fill(removalTheta, 0);
                Collections.fill(insertionRewards, 0.0);
                Collections.fill(insertionTheta, 0);
                Collections.fill(noiseRewards, 0.0);
                Collections.fill(noiseTheta, 0);
            }

            // Cool down temperature for simulated annealing (prevent underflow)
            tCurrent = Math.max(1e-10, tCurrent * params.getC());
            totalIterationNum++;
            
            if (stopIfAllRequestsCoped && sBest.getRequestBank().isEmpty()) {
                break;
            }
        }

        // Return the best solution found
        return new AlnsResult(sBest, totalIterationNum);
    }
}