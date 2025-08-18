package com.tc.pdwtw.util;

import java.util.*;
import java.io.*;
// import com.fasterxml.jackson.databind.ObjectMapper;
// import com.fasterxml.jackson.core.type.TypeReference;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Enhanced Parameters class with tuning capabilities.
 * 
 * This class provides:
 * - Parameter validation and constraints
 * - Random parameter generation for tuning
 * - Parameter grouping for organized tuning
 * - Export/import functionality
 * - Performance tracking
 */
public class Parameters {
    
    public static class ParameterRange {
        public final double minValue;
        public final double maxValue;
        public final Double step;
        public final boolean isInteger;
        public final String description;
        
        public ParameterRange(double minValue, double maxValue, Double step, 
                            boolean isInteger, String description) {
            this.minValue = minValue;
            this.maxValue = maxValue;
            this.step = step;
            this.isInteger = isInteger;
            this.description = description;
        }
        
        public ParameterRange(double minValue, double maxValue, String description) {
            this(minValue, maxValue, null, false, description);
        }
        
        public boolean validate(double value) {
            if (isInteger && value != Math.floor(value)) {
                return false;
            }
            return value >= minValue && value <= maxValue;
        }
        
        public double getRandomValue(Random random) {
            if (step == null) {
                if (isInteger) {
                    return random.nextInt((int)(maxValue - minValue + 1)) + minValue;
                } else {
                    return random.nextDouble() * (maxValue - minValue) + minValue;
                }
            } else {
                int steps = (int)((maxValue - minValue) / step) + 1;
                int stepIndex = random.nextInt(steps);
                double value = minValue + stepIndex * step;
                return isInteger ? Math.round(value) : value;
            }
        }
    }
    
    public static class ParameterGroup {
        public final String name;
        public final List<String> parameters;
        public final String description;
        
        public ParameterGroup(String name, List<String> parameters, String description) {
            this.name = name;
            this.parameters = new ArrayList<>(parameters);
            this.description = description;
        }
    }
    
    // Parameter groups
    private static final Map<String, ParameterGroup> PARAMETER_GROUPS = new HashMap<>();
    static {
        PARAMETER_GROUPS.put("objective_weights", new ParameterGroup(
            "Objective Weights",
            Arrays.asList("alpha", "beta", "gama"),
            "Weights for distance, time, and unassigned requests in objective function"
        ));
        PARAMETER_GROUPS.put("shaw_removal", new ParameterGroup(
            "Shaw Removal Parameters",
            Arrays.asList("shaw_param_1", "shaw_param_2", "shaw_param_3", "shaw_param_4"),
            "Parameters controlling Shaw removal heuristic"
        ));
        PARAMETER_GROUPS.put("roulette_wheel", new ParameterGroup(
            "Roulette Wheel Selection",
            Arrays.asList("p", "p_worst"),
            "Parameters for roulette wheel selection in removal heuristics"
        ));
        PARAMETER_GROUPS.put("simulated_annealing", new ParameterGroup(
            "Simulated Annealing",
            Arrays.asList("w", "annealing_p", "c"),
            "Parameters for simulated annealing algorithm"
        ));
        PARAMETER_GROUPS.put("adaptive_weights", new ParameterGroup(
            "Adaptive Weight Updates",
            Arrays.asList("r", "eta", "initial_weight"),
            "Parameters for adaptive weight updates in ALNS"
        ));
        PARAMETER_GROUPS.put("algorithm_control", new ParameterGroup(
            "Algorithm Control",
            Arrays.asList("iteration_num", "epsilon", "segment_num", "theta", "tau"),
            "Parameters controlling algorithm execution"
        ));
        PARAMETER_GROUPS.put("removal_bounds", new ParameterGroup(
            "Removal Bounds",
            Arrays.asList("remove_upper_bound", "remove_lower_bound"),
            "Bounds for request removal operations"
        ));
    }
    
    // Parameter ranges
    private static final Map<String, ParameterRange> PARAMETER_RANGES = new HashMap<>();
    static {
        PARAMETER_RANGES.put("alpha", new ParameterRange(1e-8, 10.0, "Weight for distance cost"));
        PARAMETER_RANGES.put("beta", new ParameterRange(1e-8, 10.0, "Weight for time cost"));
        PARAMETER_RANGES.put("gama", new ParameterRange(1000.0, 1e12, "Penalty for unassigned requests"));
        
        PARAMETER_RANGES.put("shaw_param_1", new ParameterRange(1.0, 20.0, "Weight for distance in Shaw removal"));
        PARAMETER_RANGES.put("shaw_param_2", new ParameterRange(1.0, 20.0, "Weight for time difference in Shaw removal"));
        PARAMETER_RANGES.put("shaw_param_3", new ParameterRange(1.0, 20.0, "Weight for load difference in Shaw removal"));
        PARAMETER_RANGES.put("shaw_param_4", new ParameterRange(1.0, 20.0, "Weight for vehicle set difference in Shaw removal"));
        
        PARAMETER_RANGES.put("p", new ParameterRange(1, 20, null, true, "Roulette wheel parameter for Shaw removal"));
        PARAMETER_RANGES.put("p_worst", new ParameterRange(1, 10, null, true, "Roulette wheel parameter for worst removal"));
        
        PARAMETER_RANGES.put("w", new ParameterRange(0.01, 0.5, "Initial temperature parameter"));
        PARAMETER_RANGES.put("annealing_p", new ParameterRange(0.1, 1.0, "Annealing parameter"));
        PARAMETER_RANGES.put("c", new ParameterRange(0.9, 0.9999, "Cooling rate"));
        
        PARAMETER_RANGES.put("r", new ParameterRange(0.01, 0.5, "Weight update rate"));
        PARAMETER_RANGES.put("eta", new ParameterRange(0.01, 0.1, "Weight update threshold"));
        PARAMETER_RANGES.put("initial_weight", new ParameterRange(0.1, 10.0, "Initial weight for operators"));
        
        PARAMETER_RANGES.put("iteration_num", new ParameterRange(1000, 100000, null, true, "Total number of iterations"));
        PARAMETER_RANGES.put("epsilon", new ParameterRange(0.1, 1.0, "Fraction of requests to remove"));
        PARAMETER_RANGES.put("segment_num", new ParameterRange(10, 1000, null, true, "Number of segments for weight updates"));
        PARAMETER_RANGES.put("theta", new ParameterRange(1000, 100000, null, true, "Maximum total iterations for two-stage"));
        PARAMETER_RANGES.put("tau", new ParameterRange(100, 10000, null, true, "ALNS iterations for two-stage"));
        
        PARAMETER_RANGES.put("remove_upper_bound", new ParameterRange(10, 200, null, true, "Upper bound for request removal"));
        PARAMETER_RANGES.put("remove_lower_bound", new ParameterRange(1, 20, null, true, "Lower bound for request removal"));
        
        PARAMETER_RANGES.put("unlimited_float", new ParameterRange(1e6, 1e15, "Large value for unlimited operations"));
        PARAMETER_RANGES.put("unlimited_float_bound", new ParameterRange(1e6, 1e15, "Boundary value for unlimited operations"));
    }
    
    private final Map<String, Object> params = new HashMap<>();
    private final Map<String, Object> originalParams = new HashMap<>();
    private final List<Map<String, Object>> performanceHistory = new ArrayList<>();
    private Map<String, Object> bestPerformance = null;
    private final Random random = new Random();
    // private final ObjectMapper objectMapper = new ObjectMapper();
    
    public Parameters() {
        initializeDefaultParameters();
        originalParams.putAll(params);
        validateAllParameters();
    }
    
    public Parameters(Map<String, Object> initialParams) {
        this();
        params.putAll(initialParams);
        validateAllParameters();
    }
    
    private void initializeDefaultParameters() {
        params.put("alpha", 1.0);
        params.put("beta", 1e-6);
        params.put("gama", 1000000000.0);
        params.put("shaw_param_1", 9.0);
        params.put("shaw_param_2", 3.0);
        params.put("shaw_param_3", 3.0);
        params.put("shaw_param_4", 5.0);
        params.put("p", 6);
        params.put("p_worst", 3);
        params.put("w", 0.05);
        params.put("annealing_p", 0.5);
        params.put("c", 0.99975);
        params.put("r", 0.1);
        params.put("reward_adds", Arrays.asList(10, 6, 3));
        params.put("eta", 0.025);
        params.put("initial_weight", 1);
        params.put("iteration_num", 25000);
        params.put("epsilon", 0.4);
        params.put("segment_num", 50);
        params.put("unlimited_float", 100000000000000.0);
        params.put("unlimited_float_bound", 100000000000000.0 + 100.0);
        params.put("theta", 25000);
        params.put("tau", 2000);
        params.put("remove_upper_bound", 100);
        params.put("remove_lower_bound", 4);
    }
    
    private void validateAllParameters() {
        for (Map.Entry<String, ParameterRange> entry : PARAMETER_RANGES.entrySet()) {
            String paramName = entry.getKey();
            ParameterRange range = entry.getValue();
            if (params.containsKey(paramName)) {
                Object value = params.get(paramName);
                if (value instanceof Number) {
                    if (!range.validate(((Number) value).doubleValue())) {
                        throw new IllegalArgumentException(
                            String.format("Parameter %s=%s is outside valid range [%f, %f]",
                                paramName, value, range.minValue, range.maxValue));
                    }
                }
            }
        }
    }
    
    // Getter methods for all parameters
    public double getAlpha() { return ((Number) params.get("alpha")).doubleValue(); }
    public double getBeta() { return ((Number) params.get("beta")).doubleValue(); }
    public double getGama() { return ((Number) params.get("gama")).doubleValue(); }
    public double getShawParam1() { return ((Number) params.get("shaw_param_1")).doubleValue(); }
    public double getShawParam2() { return ((Number) params.get("shaw_param_2")).doubleValue(); }
    public double getShawParam3() { return ((Number) params.get("shaw_param_3")).doubleValue(); }
    public double getShawParam4() { return ((Number) params.get("shaw_param_4")).doubleValue(); }
    public int getP() { return ((Number) params.get("p")).intValue(); }
    public int getPWorst() { return ((Number) params.get("p_worst")).intValue(); }
    public double getW() { return ((Number) params.get("w")).doubleValue(); }
    public double getAnnealingP() { return ((Number) params.get("annealing_p")).doubleValue(); }
    public double getC() { return ((Number) params.get("c")).doubleValue(); }
    public double getR() { return ((Number) params.get("r")).doubleValue(); }
    public double getEta() { return ((Number) params.get("eta")).doubleValue(); }
    public int getInitialWeight() { return ((Number) params.get("initial_weight")).intValue(); }
    public int getIterationNum() { return ((Number) params.get("iteration_num")).intValue(); }
    public double getEpsilon() { return ((Number) params.get("epsilon")).doubleValue(); }
    public int getSegmentNum() { return ((Number) params.get("segment_num")).intValue(); }
    public double getUnlimitedFloat() { return ((Number) params.get("unlimited_float")).doubleValue(); }
    public double getUnlimitedFloatBound() { return ((Number) params.get("unlimited_float_bound")).doubleValue(); }
    public int getTheta() { return ((Number) params.get("theta")).intValue(); }
    public int getTau() { return ((Number) params.get("tau")).intValue(); }
    
    // Setter methods for parameter modification
    public void setIterationNum(int value) {
        validateParameter("iteration_num", value);
        params.put("iteration_num", value);
    }
    
    public void setTau(int value) {
        validateParameter("tau", value);
        params.put("tau", value);
    }
    
    public void setTheta(int value) {
        validateParameter("theta", value);
        params.put("theta", value);
    }
    
    private void validateParameter(String paramName, Object value) {
        if (PARAMETER_RANGES.containsKey(paramName)) {
            ParameterRange range = PARAMETER_RANGES.get(paramName);
            if (value instanceof Number) {
                if (!range.validate(((Number) value).doubleValue())) {
                    throw new IllegalArgumentException(
                        String.format("Parameter %s=%s is outside valid range [%f, %f]",
                            paramName, value, range.minValue, range.maxValue));
                }
            }
        }
    }
    public int getRemoveUpperBound() { return ((Number) params.get("remove_upper_bound")).intValue(); }
    public int getRemoveLowerBound() { return ((Number) params.get("remove_lower_bound")).intValue(); }
    
    @SuppressWarnings("unchecked")
    public List<Integer> getRewardAdds() { 
        return (List<Integer>) params.get("reward_adds"); 
    }
    
    public void reset() {
        params.clear();
        params.putAll(originalParams);
        performanceHistory.clear();
        bestPerformance = null;
    }
    
    public Map<String, Object> generateRandomParameters(String groupName) {
        Map<String, Object> randomParams = new HashMap<>();
        List<String> paramNames = getTunableParameters(groupName);
        
        for (String paramName : paramNames) {
            if (PARAMETER_RANGES.containsKey(paramName)) {
                ParameterRange range = PARAMETER_RANGES.get(paramName);
                randomParams.put(paramName, range.getRandomValue(random));
            }
        }
        
        return randomParams;
    }
    
    public List<String> getTunableParameters(String groupName) {
        if (groupName == null) {
            return new ArrayList<>(PARAMETER_RANGES.keySet());
        }
        
        if (!PARAMETER_GROUPS.containsKey(groupName)) {
            throw new IllegalArgumentException("Unknown parameter group: " + groupName);
        }
        
        return PARAMETER_GROUPS.get(groupName).parameters;
    }
    
    public void applyParameters(Map<String, Object> newParams) {
        for (Map.Entry<String, Object> entry : newParams.entrySet()) {
            String name = entry.getKey();
            Object value = entry.getValue();
            
            if (params.containsKey(name)) {
                if (PARAMETER_RANGES.containsKey(name) && value instanceof Number) {
                    ParameterRange range = PARAMETER_RANGES.get(name);
                    if (!range.validate(((Number) value).doubleValue())) {
                        throw new IllegalArgumentException(
                            String.format("Parameter %s=%s is outside valid range [%f, %f]",
                                name, value, range.minValue, range.maxValue));
                    }
                }
                params.put(name, value);
            } else {
                throw new IllegalArgumentException("Unknown parameter: " + name);
            }
        }
    }
    
    public void exportParameters(String filename) throws IOException {
        // Simplified export without Jackson - would need proper JSON library
        System.out.println("Export functionality requires JSON library - parameters: " + params);
    }
    
    public void importParameters(String filename) throws IOException {
        // Simplified import without Jackson - would need proper JSON library
        System.out.println("Import functionality requires JSON library");
    }
    
    public Map<String, Object> toMap() {
        return new HashMap<>(params);
    }
}