#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2024 cauchy1988

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import random
import math
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Optional, Tuple, Any, TypeVar, Generic
from dataclasses import dataclass, field
from enum import Enum

from meta import Meta
from solution import PDWTWSolution

# Type variables for generic operations
T = TypeVar('T')  # Solution type
R = TypeVar('R')  # Reward type


class AcceptanceStrategy(Enum):
    """Different acceptance strategies for LNS"""
    ALWAYS = "always"
    BETTER_ONLY = "better_only"
    SIMULATED_ANNEALING = "simulated_annealing"
    PROBABILISTIC = "probabilistic"


class RewardStrategy(Enum):
    """Different reward strategies for operators"""
    SIMPLE = "simple"
    ADAPTIVE = "adaptive"
    RANK_BASED = "rank_based"


@dataclass
class OperatorConfig:
    """Configuration for a single operator"""
    name: str
    function: Callable
    initial_weight: float = 1.0
    min_weight: float = 0.0
    max_weight: float = float('inf')
    description: str = ""


@dataclass
class LNSConfig:
    """Configuration for LNS algorithm"""
    # Basic parameters
    max_iterations: int = 1000
    segment_length: int = 100
    
    # Removal and insertion bounds
    removal_lower_bound: int = 1
    removal_upper_bound: int = 10
    removal_epsilon: float = 0.4
    
    # Temperature parameters (for simulated annealing)
    initial_temperature: Optional[float] = None
    cooling_rate: float = 0.99975
    annealing_parameter: float = 0.5
    
    # Acceptance parameters
    acceptance_strategy: AcceptanceStrategy = AcceptanceStrategy.SIMULATED_ANNEALING
    acceptance_threshold: float = 0.1
    
    # Reward parameters
    reward_strategy: RewardStrategy = RewardStrategy.ADAPTIVE
    reward_rates: List[float] = field(default_factory=lambda: [33, 9, 13])
    weight_update_rate: float = 0.1
    
    # Noise parameters
    use_noise: bool = False
    noise_eta: float = 0.025
    
    # Parallel execution
    enable_parallel: bool = False
    max_workers: int = 4


class AcceptanceCriterion(ABC, Generic[T]):
    """Abstract base class for acceptance criteria"""
    
    @abstractmethod
    def should_accept(self, current_solution: T, new_solution: T, 
                     temperature: Optional[float] = None) -> bool:
        """Determine if a new solution should be accepted"""
        pass


class AlwaysAccept(AcceptanceCriterion[T]):
    """Always accept new solutions"""
    
    def should_accept(self, current_solution: T, new_solution: T, 
                     temperature: Optional[float] = None) -> bool:
        return True


class BetterOnlyAccept(AcceptanceCriterion[T]):
    """Only accept better solutions"""
    
    def should_accept(self, current_solution: T, new_solution: T, 
                     temperature: Optional[float] = None) -> bool:
        return new_solution.objective_cost <= current_solution.objective_cost


class SimulatedAnnealingAccept(AcceptanceCriterion[T]):
    """Simulated annealing acceptance criterion"""
    
    def should_accept(self, current_solution: T, new_solution: T, 
                     temperature: Optional[float] = None) -> bool:
        if new_solution.objective_cost <= current_solution.objective_cost:
            return True
        
        if temperature is None:
            return False
        
        delta_cost = new_solution.objective_cost - current_solution.objective_cost
        accept_probability = math.exp(-delta_cost / temperature)
        return random.random() <= accept_probability


class ProbabilisticAccept(AcceptanceCriterion[T]):
    """Probabilistic acceptance criterion"""
    
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold
    
    def should_accept(self, current_solution: T, new_solution: T, 
                     temperature: Optional[float] = None) -> bool:
        if new_solution.objective_cost <= current_solution.objective_cost:
            return True
        
        return random.random() <= self.threshold


class RewardMechanism(ABC, Generic[T]):
    """Abstract base class for reward mechanisms"""
    
    @abstractmethod
    def calculate_rewards(self, operators: List[OperatorConfig], 
                         performances: List[Dict[str, Any]]) -> List[float]:
        """Calculate rewards for operators based on their performance"""
        pass


class SimpleReward(RewardMechanism[T]):
    """Simple reward mechanism"""
    
    def __init__(self, reward_rates: List[float]):
        self.reward_rates = reward_rates
    
    def calculate_rewards(self, operators: List[OperatorConfig], 
                         performances: List[Dict[str, Any]]) -> List[float]:
        rewards = [0.0] * len(operators)
        
        for perf in performances:
            if perf.get("is_new_best", False):
                rewards[perf["operator_index"]] += self.reward_rates[0]
            elif perf.get("is_accepted", False):
                rewards[perf["operator_index"]] += self.reward_rates[1]
            else:
                rewards[perf["operator_index"]] += self.reward_rates[2]
        
        return rewards


class AdaptiveReward(RewardMechanism[T]):
    """Adaptive reward mechanism"""
    
    def __init__(self, reward_rates: List[float], update_rate: float):
        self.reward_rates = reward_rates
        self.update_rate = update_rate
    
    def calculate_rewards(self, operators: List[OperatorConfig], 
                         performances: List[Dict[str, Any]]) -> List[float]:
        rewards = [0.0] * len(operators)
        
        for perf in performances:
            if perf.get("is_new_best", False):
                rewards[perf["operator_index"]] += self.reward_rates[0]
            elif perf.get("is_accepted", False):
                rewards[perf["operator_index"]] += self.reward_rates[1]
            else:
                rewards[perf["operator_index"]] += self.reward_rates[2]
        
        return rewards


class LNSFramework(Generic[T]):
    """Generic Large Neighborhood Search Framework"""
    
    def __init__(self, config: LNSConfig):
        self.config = config
        self.removal_operators: List[OperatorConfig] = []
        self.insertion_operators: List[OperatorConfig] = []
        self.acceptance_criterion: AcceptanceCriterion[T] = self._create_acceptance_criterion()
        self.reward_mechanism: RewardMechanism[T] = self._create_reward_mechanism()
        
        # State tracking
        self.iteration_count = 0
        self.best_solution: Optional[T] = None
        self.current_solution: Optional[T] = None
        self.accepted_solutions = set()
        
        # Performance tracking
        self.removal_performances: List[Dict[str, Any]] = []
        self.insertion_performances: List[Dict[str, Any]] = []
    
    def _create_acceptance_criterion(self) -> AcceptanceCriterion[T]:
        """Create acceptance criterion based on configuration"""
        if self.config.acceptance_strategy == AcceptanceStrategy.ALWAYS:
            return AlwaysAccept()
        elif self.config.acceptance_strategy == AcceptanceStrategy.BETTER_ONLY:
            return BetterOnlyAccept()
        elif self.config.acceptance_strategy == AcceptanceStrategy.SIMULATED_ANNEALING:
            return SimulatedAnnealingAccept()
        elif self.config.acceptance_strategy == AcceptanceStrategy.PROBABILISTIC:
            return ProbabilisticAccept(self.config.acceptance_threshold)
        else:
            raise ValueError(f"Unknown acceptance strategy: {self.config.acceptance_strategy}")
    
    def _create_reward_mechanism(self) -> RewardMechanism[T]:
        """Create reward mechanism based on configuration"""
        if self.config.reward_strategy == RewardStrategy.SIMPLE:
            return SimpleReward(self.config.reward_rates)
        elif self.config.reward_strategy == RewardStrategy.ADAPTIVE:
            return AdaptiveReward(self.config.reward_rates, self.config.weight_update_rate)
        else:
            raise ValueError(f"Unknown reward strategy: {self.config.reward_strategy}")
    
    def add_removal_operator(self, operator: OperatorConfig) -> None:
        """Add a removal operator to the framework"""
        self.removal_operators.append(operator)
    
    def add_insertion_operator(self, operator: OperatorConfig) -> None:
        """Add an insertion operator to the framework"""
        self.insertion_operators.append(operator)
    
    def _select_operator(self, operators: List[OperatorConfig]) -> Tuple[OperatorConfig, int]:
        """Select an operator using weighted random selection"""
        if not operators:
            raise ValueError("No operators available")
        
        weights = [op.initial_weight for op in operators]
        selected_index = random.choices(range(len(operators)), weights=weights, k=1)[0]
        return operators[selected_index], selected_index
    
    def _calculate_removal_size(self, solution: T) -> int:
        """Calculate the number of elements to remove"""
        if hasattr(solution, 'meta_obj') and hasattr(solution.meta_obj, 'requests'):
            requests_num = len(solution.meta_obj.requests)
            q_upper = min(self.config.removal_upper_bound, 
                         int(self.config.removal_epsilon * requests_num))
            return random.randint(self.config.removal_lower_bound, q_upper)
        return random.randint(self.config.removal_lower_bound, self.config.removal_upper_bound)
    
    def _compute_temperature(self, solution: T) -> float:
        """Compute current temperature for simulated annealing"""
        if self.config.initial_temperature is None:
            if hasattr(solution, 'objective_cost_without_request_bank'):
                z0 = solution.objective_cost_without_request_bank
                delta = self.config.annealing_parameter * z0
                self.config.initial_temperature = -delta / math.log(0.5)
            else:
                self.config.initial_temperature = 100.0
        
        return self.config.initial_temperature * (self.config.cooling_rate ** self.iteration_count)
    
    def _update_weights(self, operators: List[OperatorConfig], 
                       performances: List[Dict[str, Any]]) -> None:
        """Update operator weights based on performance"""
        if not performances:
            return
        
        rewards = self.reward_mechanism.calculate_rewards(operators, performances)
        
        for i, (operator, reward) in enumerate(zip(operators, rewards)):
            # Simple weight update rule
            new_weight = (1 - self.config.weight_update_rate) * operator.initial_weight + \
                        self.config.weight_update_rate * reward
            
            # Apply bounds
            new_weight = max(self.config.min_weight, 
                           min(self.config.max_weight, new_weight))
            
            operator.initial_weight = new_weight
    
    def solve(self, initial_solution: T) -> T:
        """Execute the LNS algorithm"""
        if not self.removal_operators or not self.insertion_operators:
            raise ValueError("Must have at least one removal and one insertion operator")
        
        self.best_solution = initial_solution.copy()
        self.current_solution = initial_solution.copy()
        self.iteration_count = 0
        
        for iteration in range(self.config.max_iterations):
            self.iteration_count = iteration
            
            # Select operators
            removal_op, removal_idx = self._select_operator(self.removal_operators)
            insertion_op, insertion_idx = self._select_operator(self.insertion_operators)
            
            # Calculate removal size
            q = self._calculate_removal_size(self.current_solution)
            
            # Create candidate solution
            candidate_solution = self.current_solution.copy()
            
            # Apply removal
            removal_op.function(candidate_solution, q)
            
            # Apply insertion
            insertion_op.function(candidate_solution, q)
            
            # Check if solution was already accepted
            if hasattr(candidate_solution, 'finger_print'):
                if candidate_solution.finger_print in self.accepted_solutions:
                    continue
                self.accepted_solutions.add(candidate_solution.finger_print)
            
            # Determine acceptance
            temperature = self._compute_temperature(self.current_solution)
            is_accepted = self.acceptance_criterion.should_accept(
                self.current_solution, candidate_solution, temperature
            )
            
            # Update best solution
            is_new_best = False
            if hasattr(candidate_solution, 'objective_cost'):
                if candidate_solution.objective_cost < self.best_solution.objective_cost:
                    self.best_solution = candidate_solution.copy()
                    is_new_best = True
            
            # Record performance
            removal_perf = {
                "operator_index": removal_idx,
                "is_new_best": is_new_best,
                "is_accepted": is_accepted
            }
            insertion_perf = {
                "operator_index": insertion_idx,
                "is_new_best": is_new_best,
                "is_accepted": is_accepted
            }
            
            self.removal_performances.append(removal_perf)
            self.insertion_performances.append(insertion_perf)
            
            # Update current solution if accepted
            if is_accepted:
                self.current_solution = candidate_solution.copy()
            
            # Update weights periodically
            if (iteration + 1) % self.config.segment_length == 0:
                self._update_weights(self.removal_operators, self.removal_performances)
                self._update_weights(self.insertion_operators, self.insertion_performances)
                
                # Reset performance tracking
                self.removal_performances.clear()
                self.insertion_performances.clear()
        
        return self.best_solution
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get algorithm statistics"""
        return {
            "iterations": self.iteration_count,
            "best_solution": self.best_solution,
            "current_solution": self.current_solution,
            "accepted_solutions_count": len(self.accepted_solutions),
            "removal_operators": [op.name for op in self.removal_operators],
            "insertion_operators": [op.name for op in self.insertion_operators]
        }


# Factory functions for common LNS variants
def create_alns_framework(config: Optional[LNSConfig] = None) -> LNSFramework:
    """Create an ALNS framework with default configuration"""
    if config is None:
        config = LNSConfig(
            acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING,
            reward_strategy=RewardStrategy.ADAPTIVE,
            use_noise=True
        )
    
    framework = LNSFramework(config)
    
    # Add default ALNS operators
    from removal import shaw_removal, random_removal, worst_removal
    from insertion import basic_greedy_insertion, regret_insertion_wrapper
    
    framework.add_removal_operator(OperatorConfig("shaw_removal", shaw_removal))
    framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
    framework.add_removal_operator(OperatorConfig("worst_removal", worst_removal))
    
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
    framework.add_insertion_operator(OperatorConfig("regret_2_insertion", regret_insertion_wrapper(2)))
    framework.add_insertion_operator(OperatorConfig("regret_3_insertion", regret_insertion_wrapper(3)))
    framework.add_insertion_operator(OperatorConfig("regret_4_insertion", regret_insertion_wrapper(4)))
    
    return framework


def create_simple_lns_framework(config: Optional[LNSConfig] = None) -> LNSFramework:
    """Create a simple LNS framework"""
    if config is None:
        config = LNSConfig(
            acceptance_strategy=AcceptanceStrategy.BETTER_ONLY,
            reward_strategy=RewardStrategy.SIMPLE
        )
    
    framework = LNSFramework(config)
    
    # Add simple operators
    from removal import random_removal
    from insertion import basic_greedy_insertion
    
    framework.add_removal_operator(OperatorConfig("random_removal", random_removal))
    framework.add_insertion_operator(OperatorConfig("greedy_insertion", basic_greedy_insertion))
    
    return framework
