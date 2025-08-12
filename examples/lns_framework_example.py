#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/12 20:45
# @Author  : Tang Chao
# @File    : lns_framework_example.py
# @Software: PyCharm
"""
Example script demonstrating the new LNS Framework.

This script shows how to:
1. Use the generic LNS framework
2. Configure different acceptance strategies
3. Use different reward mechanisms
4. Create custom LNS variants
5. Compare different configurations
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from lns_framework import (
    LNSFramework, LNSConfig, OperatorConfig,
    AcceptanceStrategy, RewardStrategy,
    create_alns_framework, create_simple_lns_framework
)
from removal import shaw_removal, random_removal, worst_removal
from insertion import basic_greedy_insertion, regret_insertion_wrapper


def example_basic_usage():
    """Basic usage of the LNS framework"""
    print("=== Basic LNS Framework Usage ===")
    
    # Create a simple configuration
    config = LNSConfig(
        max_iterations=100,
        segment_length=20,
        acceptance_strategy=AcceptanceStrategy.BETTER_ONLY,
        reward_strategy=RewardStrategy.SIMPLE
    )
    
    # Create framework
    framework = LNSFramework(config)
    
    # Add operators
    framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
    
    print(f"Framework created with {len(framework.removal_operators)} removal and {len(framework.insertion_operators)} insertion operators")
    print(f"Configuration: {config.max_iterations} iterations, {config.segment_length} segment length")
    
    return framework


def example_alns_framework():
    """Example of using the pre-configured ALNS framework"""
    print("\n=== ALNS Framework Example ===")
    
    # Create ALNS framework with custom configuration
    config = LNSConfig(
        max_iterations=200,
        segment_length=50,
        acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING,
        reward_strategy=RewardStrategy.ADAPTIVE,
        cooling_rate=0.9995,
        weight_update_rate=0.15
    )
    
    framework = create_alns_framework(config)
    
    print(f"ALNS framework created with {len(framework.removal_operators)} removal operators")
    print(f"Insertion operators: {[op.name for op in framework.insertion_operators]}")
    print(f"Acceptance strategy: {config.acceptance_strategy.value}")
    print(f"Reward strategy: {config.reward_strategy.value}")
    
    return framework


def example_custom_lns():
    """Example of creating a custom LNS variant"""
    print("\n=== Custom LNS Variant Example ===")
    
    # Create custom configuration
    config = LNSConfig(
        max_iterations=150,
        segment_length=30,
        acceptance_strategy=AcceptanceStrategy.PROBABILISTIC,
        acceptance_threshold=0.2,
        reward_strategy=RewardStrategy.SIMPLE,
        removal_lower_bound=2,
        removal_upper_bound=8
    )
    
    framework = LNSFramework(config)
    
    # Add custom operator combination
    framework.add_removal_operator(OperatorConfig("shaw_removal", shaw_removal, initial_weight=2.0))
    framework.add_removal_operator(OperatorConfig("worst_removal", worst_removal, initial_weight=1.5))
    
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion, initial_weight=1.0))
    framework.add_insertion_operator(OperatorConfig("regret_3_insertion", regret_insertion_wrapper(3), initial_weight=1.5))
    
    print(f"Custom LNS created with configuration:")
    print(f"  Acceptance: {config.acceptance_strategy.value} (threshold: {config.acceptance_threshold})")
    print(f"  Reward: {config.reward_strategy.value}")
    print(f"  Removal bounds: [{config.removal_lower_bound}, {config.removal_upper_bound}]")
    print(f"  Operators: {len(framework.removal_operators)} removal, {len(framework.insertion_operators)} insertion")
    
    return framework


def example_acceptance_strategies():
    """Compare different acceptance strategies"""
    print("\n=== Acceptance Strategies Comparison ===")
    
    strategies = [
        (AcceptanceStrategy.ALWAYS, "Always Accept"),
        (AcceptanceStrategy.BETTER_ONLY, "Better Only"),
        (AcceptanceStrategy.SIMULATED_ANNEALING, "Simulated Annealing"),
        (AcceptanceStrategy.PROBABILISTIC, "Probabilistic (0.3)")
    ]
    
    for strategy, name in strategies:
        config = LNSConfig(
            max_iterations=50,
            segment_length=10,
            acceptance_strategy=strategy,
            acceptance_threshold=0.3 if strategy == AcceptanceStrategy.PROBABILISTIC else 0.1
        )
        
        framework = LNSFramework(config)
        framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
        framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
        
        print(f"  {name}: {strategy.value}")


def example_reward_mechanisms():
    """Compare different reward mechanisms"""
    print("\n=== Reward Mechanisms Comparison ===")
    
    mechanisms = [
        (RewardStrategy.SIMPLE, "Simple Reward"),
        (RewardStrategy.ADAPTIVE, "Adaptive Reward")
    ]
    
    for mechanism, name in mechanisms:
        config = LNSConfig(
            max_iterations=50,
            segment_length=10,
            reward_strategy=mechanism,
            weight_update_rate=0.1
        )
        
        framework = LNSFramework(config)
        framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
        framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
        
        print(f"  {name}: {mechanism.value}")


def example_operator_weights():
    """Example of configuring operator weights"""
    print("\n=== Operator Weights Configuration ===")
    
    framework = LNSFramework(LNSConfig(max_iterations=100, segment_length=20))
    
    # Add operators with different weights
    framework.add_removal_operator(OperatorConfig(
        "shaw_removal", shaw_removal, 
        initial_weight=3.0, 
        description="High weight for Shaw removal"
    ))
    framework.add_removal_operator(OperatorConfig(
        "random_removal", random_removal, 
        initial_weight=1.0, 
        description="Standard weight for random removal"
    ))
    framework.add_removal_operator(OperatorConfig(
        "worst_removal", worst_removal, 
        initial_weight=2.0, 
        description="Medium weight for worst removal"
    ))
    
    framework.add_insertion_operator(OperatorConfig(
        "greedy_insertion", basic_greedy_insertion, 
        initial_weight=1.5,
        description="Standard weight for greedy insertion"
    ))
    framework.add_insertion_operator(OperatorConfig(
        "regret_3_insertion", regret_insertion_wrapper(3), 
        initial_weight=2.5,
        description="High weight for regret-3 insertion"
    ))
    
    print("Operators configured with different weights:")
    for op in framework.removal_operators:
        print(f"  Removal: {op.name} (weight: {op.initial_weight}) - {op.description}")
    
    for op in framework.insertion_operators:
        print(f"  Insertion: {op.name} (weight: {op.initial_weight}) - {op.description}")
    
    return framework


def example_parallel_configuration():
    """Example of parallel execution configuration"""
    print("\n=== Parallel Execution Configuration ===")
    
    config = LNSConfig(
        max_iterations=500,
        segment_length=100,
        enable_parallel=True,
        max_workers=4,
        acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING,
        reward_strategy=RewardStrategy.ADAPTIVE
    )
    
    framework = LNSFramework(config)
    
    # Add multiple operators for parallel execution
    framework.add_removal_operator(OperatorConfig("shaw_removal", shaw_removal))
    framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
    framework.add_removal_operator(OperatorConfig("worst_removal", worst_removal))
    
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
    framework.add_insertion_operator(OperatorConfig("regret_2_insertion", regret_insertion_wrapper(2)))
    framework.add_insertion_operator(OperatorConfig("regret_3_insertion", regret_insertion_wrapper(3)))
    framework.add_insertion_operator(OperatorConfig("regret_4_insertion", regret_insertion_wrapper(4)))
    
    print(f"Parallel LNS configured:")
    print(f"  Workers: {config.max_workers}")
    print(f"  Operators: {len(framework.removal_operators)} removal, {len(framework.insertion_operators)} insertion")
    print(f"  Note: Parallel execution requires additional implementation")
    
    return framework


def example_statistics_and_monitoring():
    """Example of using statistics and monitoring features"""
    print("\n=== Statistics and Monitoring Example ===")
    
    # Create a simple framework for demonstration
    framework = LNSFramework(LNSConfig(max_iterations=50, segment_length=10))
    framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
    
    print("Framework created with monitoring capabilities")
    print("Available statistics:")
    print("  - Iteration count")
    print("  - Best solution")
    print("  - Current solution")
    print("  - Accepted solutions count")
    print("  - Operator lists")
    
    return framework


def main():
    """Main function to run all examples"""
    print("LNS Framework Examples")
    print("=" * 60)
    
    try:
        # Run all examples
        framework1 = example_basic_usage()
        framework2 = example_alns_framework()
        framework3 = example_custom_lns()
        example_acceptance_strategies()
        example_reward_mechanisms()
        framework4 = example_operator_weights()
        framework5 = example_parallel_configuration()
        framework6 = example_statistics_and_monitoring()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Generic LNS framework with configurable components")
        print("✓ Multiple acceptance strategies (Always, Better Only, SA, Probabilistic)")
        print("✓ Multiple reward mechanisms (Simple, Adaptive)")
        print("✓ Configurable operator weights and descriptions")
        print("✓ Pre-configured ALNS and Simple LNS variants")
        print("✓ Parallel execution configuration support")
        print("✓ Statistics and monitoring capabilities")
        print("✓ Extensible architecture for custom LNS variants")
        
        print("\nNext Steps:")
        print("1. Use create_alns_framework() for standard ALNS")
        print("2. Use create_simple_lns_framework() for basic LNS")
        print("3. Create custom configurations with LNSConfig")
        print("4. Extend with custom operators and strategies")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
