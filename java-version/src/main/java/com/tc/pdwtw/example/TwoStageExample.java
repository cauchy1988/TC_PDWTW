package com.tc.pdwtw.example;

import com.tc.pdwtw.algorithm.TwoStage;
import com.tc.pdwtw.benchmark.LiLimBenchmarkReader;
import com.tc.pdwtw.model.*;
import java.util.Map;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Two-stage algorithm example using Li & Lim benchmark data
 */
public class TwoStageExample {

    public static void main(String[] args) {
        System.out.println("Two-Stage Algorithm Example for Li & Lim Dataset");
        System.out.println("===============================================");
        
        try {
            // Read benchmark data
            String filePath = args.length > 0 ? args[0] : "benchmark/LR1_2_1.txt";
            LiLimBenchmarkReader reader = new LiLimBenchmarkReader();
            reader.readFile(filePath);
            reader.printSummary();
            
            // Validate data
            if (reader.validateData()) {
                System.out.println("\n✅ Li & Lim data validation passed!");
            } else {
                System.out.println("\n❌ Li & Lim data validation failed!");
                System.exit(-1);
            }
            
            // Get meta object and create initial solution
            Meta metaObj = reader.getMetaObj();
            PDWTWSolution initialSolution = new PDWTWSolution(metaObj);
            
            System.out.println("\nInitial Solution:");
            System.out.println("  - Total requests: " + metaObj.getRequests().size());
            System.out.println("  - Total vehicles: " + metaObj.getVehicles().size());
            System.out.println("  - Unassigned requests: " + initialSolution.getRequestBank().size());
            System.out.println("  - Initial objective cost: " + initialSolution.getObjectiveCost());
            
            // Run two-stage algorithm
            System.out.println("\n🚀 Starting Two-Stage Algorithm...");
            long startTime = System.currentTimeMillis();
            
            PDWTWSolution finalSolution = TwoStage.twoStageAlgorithmInHomogeneousFleet(initialSolution);
            
            long endTime = System.currentTimeMillis();
            double executionTime = (endTime - startTime) / 1000.0;
            
            // Print results
            System.out.println("\n📊 Final Results:");
            System.out.println("================");
            System.out.println("  - Vehicles used: " + finalSolution.getPaths().size());
            System.out.println("  - Unassigned requests: " + finalSolution.getRequestBank().size());
            System.out.println("  - Total distance cost: " + String.format("%.2f", finalSolution.getDistanceCost()));
            System.out.println("  - Total time cost: " + String.format("%.2f", finalSolution.getTimeCost()));
            System.out.println("  - Final objective cost: " + String.format("%.2f", finalSolution.getObjectiveCost()));
            System.out.println("  - Execution time: " + String.format("%.2f", executionTime) + " seconds");
            
            // Check if all requests are assigned
            if (finalSolution.getRequestBank().isEmpty()) {
                System.out.println("\n🎉 All requests successfully assigned!");
            } else {
                System.out.println("\n⚠️  Some requests remain unassigned: " + finalSolution.getRequestBank().size());
            }
            
            // Print route summary
            System.out.println("\n🚛 Vehicle Routes Summary:");
            System.out.println("=========================");
            for (Map.Entry<Integer, Path> entry : finalSolution.getPaths().entrySet()) {
                Integer vehicleId = entry.getKey();
                Path path = entry.getValue();
                System.out.println("  Vehicle " + vehicleId + ": " + path.getRoute().size() + " nodes, " +
                                 "distance: " + String.format("%.2f", path.getWholeDistanceCost()) + 
                                 ", time: " + String.format("%.2f", path.getWholeTimeCost()));
            }
            
            System.out.println("\n✅ Two-Stage Algorithm completed successfully!");
            
        } catch (Exception e) {
            System.err.println("❌ Error during Two-Stage Algorithm execution:");
            e.printStackTrace();
            System.exit(-1);
        }
    }
}