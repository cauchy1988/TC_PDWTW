#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/8/12 21:15
# @Author  : Tang Chao
# @File    : test_lns_framework.py
# @Software: PyCharm
"""
Test script for the LNS Framework.

This script tests the functionality of the new LNS framework,
including configuration, operator management, and algorithm execution.
"""

import sys
import os
import unittest
from unittest.mock import Mock, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from lns_framework import (
        LNSFramework, LNSConfig, OperatorConfig,
        AcceptanceStrategy, RewardStrategy,
        create_alns_framework, create_simple_lns_framework
    )
    from lns_framework import (
        AlwaysAccept, BetterOnlyAccept, SimulatedAnnealingAccept, ProbabilisticAccept
    )
    from lns_framework import SimpleReward, AdaptiveReward
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the LNS framework is properly installed")
    sys.exit(1)


class TestLNSConfig(unittest.TestCase):
    """Test LNSConfig class"""
    
    def test_default_configuration(self):
        """Test default configuration values"""
        config = LNSConfig()
        
        self.assertEqual(config.max_iterations, 1000)
        self.assertEqual(config.segment_length, 100)
        self.assertEqual(config.removal_lower_bound, 1)
        self.assertEqual(config.removal_upper_bound, 10)
        self.assertEqual(config.removal_epsilon, 0.4)
        self.assertEqual(config.cooling_rate, 0.99975)
        self.assertEqual(config.annealing_parameter, 0.5)
        self.assertEqual(config.acceptance_strategy, AcceptanceStrategy.SIMULATED_ANNEALING)
        self.assertEqual(config.reward_strategy, RewardStrategy.ADAPTIVE)
        self.assertEqual(config.reward_rates, [33, 9, 13])
        self.assertEqual(config.weight_update_rate, 0.1)
        self.assertFalse(config.use_noise)
        self.assertEqual(config.noise_eta, 0.025)
        self.assertFalse(config.enable_parallel)
        self.assertEqual(config.max_workers, 4)
    
    def test_custom_configuration(self):
        """Test custom configuration values"""
        config = LNSConfig(
            max_iterations=500,
            segment_length=50,
            acceptance_strategy=AcceptanceStrategy.BETTER_ONLY,
            reward_strategy=RewardStrategy.SIMPLE,
            cooling_rate=0.9995,
            weight_update_rate=0.2
        )
        
        self.assertEqual(config.max_iterations, 500)
        self.assertEqual(config.segment_length, 50)
        self.assertEqual(config.acceptance_strategy, AcceptanceStrategy.BETTER_ONLY)
        self.assertEqual(config.reward_strategy, RewardStrategy.SIMPLE)
        self.assertEqual(config.cooling_rate, 0.9995)
        self.assertEqual(config.weight_update_rate, 0.2)


class TestOperatorConfig(unittest.TestCase):
    """Test OperatorConfig class"""
    
    def test_operator_configuration(self):
        """Test operator configuration"""
        mock_function = Mock()
        
        config = OperatorConfig(
            name="test_operator",
            function=mock_function,
            initial_weight=2.5,
            min_weight=0.1,
            max_weight=10.0,
            description="Test operator for testing"
        )
        
        self.assertEqual(config.name, "test_operator")
        self.assertEqual(config.function, mock_function)
        self.assertEqual(config.initial_weight, 2.5)
        self.assertEqual(config.min_weight, 0.1)
        self.assertEqual(config.max_weight, 10.0)
        self.assertEqual(config.description, "Test operator for testing")
    
    def test_default_operator_configuration(self):
        """Test default operator configuration values"""
        mock_function = Mock()
        
        config = OperatorConfig("test_operator", mock_function)
        
        self.assertEqual(config.initial_weight, 1.0)
        self.assertEqual(config.min_weight, 0.0)
        self.assertEqual(config.max_weight, float('inf'))
        self.assertEqual(config.description, "")


class TestAcceptanceCriteria(unittest.TestCase):
    """Test acceptance criteria classes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.current_solution = Mock()
        self.current_solution.objective_cost = 100.0
        
        self.better_solution = Mock()
        self.better_solution.objective_cost = 80.0
        
        self.worse_solution = Mock()
        self.worse_solution.objective_cost = 120.0
    
    def test_always_accept(self):
        """Test AlwaysAccept criterion"""
        criterion = AlwaysAccept()
        
        # Should always accept
        self.assertTrue(criterion.should_accept(self.current_solution, self.better_solution))
        self.assertTrue(criterion.should_accept(self.current_solution, self.worse_solution))
        self.assertTrue(criterion.should_accept(self.current_solution, self.current_solution))
    
    def test_better_only_accept(self):
        """Test BetterOnlyAccept criterion"""
        criterion = BetterOnlyAccept()
        
        # Should only accept better or equal solutions
        self.assertTrue(criterion.should_accept(self.current_solution, self.better_solution))
        self.assertTrue(criterion.should_accept(self.current_solution, self.current_solution))
        self.assertFalse(criterion.should_accept(self.current_solution, self.worse_solution))
    
    def test_simulated_annealing_accept(self):
        """Test SimulatedAnnealingAccept criterion"""
        criterion = SimulatedAnnealingAccept()
        
        # Should always accept better solutions
        self.assertTrue(criterion.should_accept(self.current_solution, self.better_solution))
        self.assertTrue(criterion.should_accept(self.current_solution, self.current_solution))
        
        # Should accept worse solutions with probability based on temperature
        # At high temperature, should be more likely to accept
        high_temp = 1000.0
        low_temp = 0.1
        
        # Test with high temperature (more likely to accept)
        # Note: This is probabilistic, so we test multiple times
        accepted_count = 0
        for _ in range(100):
            if criterion.should_accept(self.current_solution, self.worse_solution, high_temp):
                accepted_count += 1
        
        # Should accept some worse solutions at high temperature
        self.assertGreater(accepted_count, 0)
        
        # Test with low temperature (less likely to accept)
        accepted_count = 0
        for _ in range(100):
            if criterion.should_accept(self.current_solution, self.worse_solution, low_temp):
                accepted_count += 1
        
        # Should accept fewer worse solutions at low temperature
        self.assertLessEqual(accepted_count, 50)
    
    def test_probabilistic_accept(self):
        """Test ProbabilisticAccept criterion"""
        criterion = ProbabilisticAccept(threshold=0.3)
        
        # Should always accept better solutions
        self.assertTrue(criterion.should_accept(self.current_solution, self.better_solution))
        self.assertTrue(criterion.should_accept(self.current_solution, self.current_solution))
        
        # Should accept worse solutions with fixed probability
        accepted_count = 0
        for _ in range(100):
            if criterion.should_accept(self.current_solution, self.worse_solution):
                accepted_count += 1
        
        # Should accept approximately 30% of worse solutions
        self.assertGreaterEqual(accepted_count, 20)
        self.assertLessEqual(accepted_count, 40)


class TestRewardMechanisms(unittest.TestCase):
    """Test reward mechanism classes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.operators = [
            OperatorConfig("op1", Mock()),
            OperatorConfig("op2", Mock()),
            OperatorConfig("op3", Mock())
        ]
    
    def test_simple_reward(self):
        """Test SimpleReward mechanism"""
        reward_rates = [10.0, 5.0, 1.0]
        mechanism = SimpleReward(reward_rates)
        
        performances = [
            {"operator_index": 0, "is_new_best": True, "is_accepted": False},
            {"operator_index": 1, "is_new_best": False, "is_accepted": True},
            {"operator_index": 2, "is_new_best": False, "is_accepted": False}
        ]
        
        rewards = mechanism.calculate_rewards(self.operators, performances)
        
        self.assertEqual(rewards[0], 10.0)  # New best
        self.assertEqual(rewards[1], 5.0)   # Accepted
        self.assertEqual(rewards[2], 1.0)   # Rejected
    
    def test_adaptive_reward(self):
        """Test AdaptiveReward mechanism"""
        reward_rates = [10.0, 5.0, 1.0]
        update_rate = 0.1
        mechanism = AdaptiveReward(reward_rates, update_rate)
        
        performances = [
            {"operator_index": 0, "is_new_best": True, "is_accepted": False},
            {"operator_index": 1, "is_new_best": False, "is_accepted": True},
            {"operator_index": 2, "is_new_best": False, "is_accepted": False}
        ]
        
        rewards = mechanism.calculate_rewards(self.operators, performances)
        
        self.assertEqual(rewards[0], 10.0)  # New best
        self.assertEqual(rewards[1], 5.0)   # Accepted
        self.assertEqual(rewards[2], 1.0)   # Rejected


class TestLNSFramework(unittest.TestCase):
    """Test LNSFramework class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = LNSConfig(
            max_iterations=10,
            segment_length=5,
            acceptance_strategy=AcceptanceStrategy.BETTER_ONLY,
            reward_strategy=RewardStrategy.SIMPLE
        )
        
        self.framework = LNSFramework(self.config)
        
        # Mock solution
        self.mock_solution = Mock()
        self.mock_solution.copy.return_value = self.mock_solution
        self.mock_solution.objective_cost = 100.0
        self.mock_solution.finger_print = "test_fingerprint"
        
        # Mock operators
        self.mock_removal = Mock()
        self.mock_insertion = Mock()
    
    def test_framework_initialization(self):
        """Test framework initialization"""
        self.assertEqual(len(self.framework.removal_operators), 0)
        self.assertEqual(len(self.framework.insertion_operators), 0)
        self.assertIsInstance(self.framework.acceptance_criterion, BetterOnlyAccept)
        self.assertIsInstance(self.framework.reward_mechanism, SimpleReward)
    
    def test_add_operators(self):
        """Test adding operators"""
        removal_op = OperatorConfig("test_removal", self.mock_removal)
        insertion_op = OperatorConfig("test_insertion", self.mock_insertion)
        
        self.framework.add_removal_operator(removal_op)
        self.framework.add_insertion_operator(insertion_op)
        
        self.assertEqual(len(self.framework.removal_operators), 1)
        self.assertEqual(len(self.framework.insertion_operators), 1)
        self.assertEqual(self.framework.removal_operators[0].name, "test_removal")
        self.assertEqual(self.framework.insertion_operators[0].name, "test_insertion")
    
    def test_operator_selection(self):
        """Test operator selection"""
        # Add operators with different weights
        removal_op1 = OperatorConfig("removal1", self.mock_removal, initial_weight=2.0)
        removal_op2 = OperatorConfig("removal2", self.mock_removal, initial_weight=1.0)
        
        self.framework.add_removal_operator(removal_op1)
        self.framework.add_removal_operator(removal_op2)
        
        # Test selection multiple times to ensure weighted selection works
        selected_ops = []
        for _ in range(100):
            op, idx = self.framework._select_operator(self.framework.removal_operators)
            selected_ops.append(idx)
        
        # Should select both operators, but op1 (weight 2.0) more frequently
        self.assertIn(0, selected_ops)
        self.assertIn(1, selected_ops)
    
    def test_calculate_removal_size(self):
        """Test removal size calculation"""
        # Test with default bounds
        size = self.framework._calculate_removal_size(self.mock_solution)
        self.assertGreaterEqual(size, self.config.removal_lower_bound)
        self.assertLessEqual(size, self.config.removal_upper_bound)
    
    def test_compute_temperature(self):
        """Test temperature computation"""
        # Test with default temperature
        temp = self.framework._compute_temperature(self.mock_solution)
        self.assertEqual(temp, 100.0)  # Default value
        
        # Test with custom initial temperature
        self.config.initial_temperature = 200.0
        framework = LNSFramework(self.config)
        temp = framework._compute_temperature(self.mock_solution)
        self.assertEqual(temp, 200.0)
    
    def test_weight_update(self):
        """Test weight update mechanism"""
        # Add operators
        removal_op = OperatorConfig("test_removal", self.mock_removal, initial_weight=1.0)
        self.framework.add_removal_operator(removal_op)
        
        # Add performance data
        performances = [{"operator_index": 0, "is_new_best": True, "is_accepted": True}]
        
        # Update weights
        self.framework._update_weights(self.framework.removal_operators, performances)
        
        # Weight should be updated (increased due to good performance)
        self.assertGreater(self.framework.removal_operators[0].initial_weight, 1.0)
    
    def test_solve_without_operators(self):
        """Test solve method without operators"""
        with self.assertRaises(ValueError):
            self.framework.solve(self.mock_solution)
    
    def test_solve_with_operators(self):
        """Test solve method with operators"""
        # Add operators
        removal_op = OperatorConfig("test_removal", self.mock_removal)
        insertion_op = OperatorConfig("test_insertion", self.mock_insertion)
        
        self.framework.add_removal_operator(removal_op)
        self.framework.add_insertion_operator(insertion_op)
        
        # Mock the operators to do nothing
        self.mock_removal.return_value = None
        self.mock_insertion.return_value = None
        
        # Solve
        result = self.framework.solve(self.mock_solution)
        
        # Should return the best solution
        self.assertEqual(result, self.mock_solution)
        
        # Should have executed the algorithm
        self.assertEqual(self.framework.iteration_count, 9)  # 0-based indexing
    
    def test_get_statistics(self):
        """Test statistics retrieval"""
        stats = self.framework.get_statistics()
        
        self.assertIn('iterations', stats)
        self.assertIn('best_solution', stats)
        self.assertIn('current_solution', stats)
        self.assertIn('accepted_solutions_count', stats)
        self.assertIn('removal_operators', stats)
        self.assertIn('insertion_operators', stats)


class TestFactoryFunctions(unittest.TestCase):
    """Test factory functions"""
    
    def test_create_alns_framework(self):
        """Test ALNS framework creation"""
        framework = create_alns_framework()
        
        self.assertIsInstance(framework, LNSFramework)
        self.assertEqual(len(framework.removal_operators), 3)  # shaw, random, worst
        self.assertEqual(len(framework.insertion_operators), 4)  # greedy + 3 regret variants
        self.assertIsInstance(framework.acceptance_criterion, SimulatedAnnealingAccept)
        self.assertIsInstance(framework.reward_mechanism, AdaptiveReward)
    
    def test_create_simple_lns_framework(self):
        """Test simple LNS framework creation"""
        framework = create_simple_lns_framework()
        
        self.assertIsInstance(framework, LNSFramework)
        self.assertEqual(len(framework.removal_operators), 1)  # random only
        self.assertEqual(len(framework.insertion_operators), 1)  # greedy only
        self.assertIsInstance(framework.acceptance_criterion, BetterOnlyAccept)
        self.assertIsInstance(framework.reward_mechanism, SimpleReward)
    
    def test_create_alns_framework_with_config(self):
        """Test ALNS framework creation with custom config"""
        config = LNSConfig(
            max_iterations=500,
            segment_length=100,
            cooling_rate=0.9995
        )
        
        framework = create_alns_framework(config)
        
        self.assertEqual(framework.config.max_iterations, 500)
        self.assertEqual(framework.config.segment_length, 100)
        self.assertEqual(framework.config.cooling_rate, 0.9995)


def run_tests():
    """Run all tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLNSConfig,
        TestOperatorConfig,
        TestAcceptanceCriteria,
        TestRewardMechanisms,
        TestLNSFramework,
        TestFactoryFunctions
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running LNS Framework Tests")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n" + "=" * 50)
        print("All tests passed! ✓")
        print("The LNS framework is working correctly.")
    else:
        print("\n" + "=" * 50)
        print("Some tests failed! ✗")
        print("Please check the test output above for details.")
    
    sys.exit(0 if success else 1)
