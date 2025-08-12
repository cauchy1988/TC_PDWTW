# LNS Framework - 架构总结

## 🎯 **项目目标**

将原有的`alns.py`重构为一个通用的**Large Neighborhood Search (LNS)框架**，让ALNS作为特例，同时支持：

- **可配置的插入/移除函数集合**
- **可配置的接受逻辑**
- **灵活的奖励机制**
- **可扩展的架构设计**

## 🏗️ **架构设计**

### **核心组件**

```
LNS Framework
├── LNSConfig (配置管理)
├── LNSFramework (主框架)
├── OperatorConfig (操作符配置)
├── AcceptanceCriterion (接受准则)
└── RewardMechanism (奖励机制)
```

### **设计原则**

1. **开闭原则**: 对扩展开放，对修改封闭
2. **单一职责**: 每个类只负责一个功能
3. **依赖倒置**: 依赖抽象而非具体实现
4. **接口隔离**: 提供最小化的接口

## 🔧 **主要功能**

### **1. 配置管理 (LNSConfig)**

```python
config = LNSConfig(
    max_iterations=1000,           # 最大迭代次数
    segment_length=100,            # 权重更新段长度
    acceptance_strategy=AcceptanceStrategy.SIMULATED_ANNEALING,  # 接受策略
    reward_strategy=RewardStrategy.ADAPTIVE,                     # 奖励策略
    cooling_rate=0.99975,          # 冷却率
    weight_update_rate=0.1         # 权重更新率
)
```

### **2. 操作符管理 (OperatorConfig)**

```python
# 添加移除操作符
framework.add_removal_operator(OperatorConfig(
    "shaw_removal", shaw_removal, 
    initial_weight=2.0,
    description="Shaw removal with high weight"
))

# 添加插入操作符
framework.add_insertion_operator(OperatorConfig(
    "regret_3_insertion", regret_insertion_wrapper(3),
    initial_weight=1.5,
    min_weight=0.1,
    max_weight=5.0
))
```

### **3. 接受策略 (AcceptanceStrategy)**

| 策略 | 描述 | 适用场景 |
|------|------|----------|
| `ALWAYS` | 总是接受 | 探索优先 |
| `BETTER_ONLY` | 只接受更好的 | 爬山算法 |
| `SIMULATED_ANNEALING` | 模拟退火 | 平衡探索与利用 |
| `PROBABILISTIC` | 概率接受 | 简单随机策略 |

### **4. 奖励机制 (RewardStrategy)**

| 机制 | 描述 | 特点 |
|------|------|------|
| `SIMPLE` | 固定奖励率 | 简单可预测 |
| `ADAPTIVE` | 自适应奖励 | 动态调整 |

## 🚀 **使用方式**

### **快速开始**

```python
from lns_framework import create_alns_framework

# 创建ALNS框架
framework = create_alns_framework()

# 求解
best_solution = framework.solve(initial_solution)
```

### **自定义配置**

```python
from lns_framework import LNSFramework, LNSConfig, OperatorConfig

# 创建自定义配置
config = LNSConfig(
    max_iterations=500,
    acceptance_strategy=AcceptanceStrategy.PROBABILISTIC,
    acceptance_threshold=0.2
)

# 创建框架
framework = LNSFramework(config)

# 添加操作符
framework.add_removal_operator(OperatorConfig("custom_removal", custom_removal))
framework.add_insertion_operator(OperatorConfig("custom_insertion", custom_insertion))

# 求解
best_solution = framework.solve(initial_solution)
```

### **扩展自定义组件**

```python
# 自定义接受准则
class CustomAcceptance(AcceptanceCriterion):
    def should_accept(self, current_solution, new_solution, temperature=None):
        # 自定义逻辑
        return custom_logic()

# 自定义奖励机制
class CustomReward(RewardMechanism):
    def calculate_rewards(self, operators, performances):
        # 自定义奖励计算
        return custom_rewards()

# 使用自定义组件
framework.acceptance_criterion = CustomAcceptance()
framework.reward_mechanism = CustomReward()
```

## 📊 **性能监控**

### **统计信息**

```python
stats = framework.get_statistics()
print(f"迭代次数: {stats['iterations']}")
print(f"最佳解: {stats['best_solution']}")
print(f"接受解数量: {stats['accepted_solutions_count']}")
print(f"移除操作符: {stats['removal_operators']}")
print(f"插入操作符: {stats['insertion_operators']}")
```

### **权重跟踪**

- 操作符权重根据性能自动调整
- 每`segment_length`次迭代更新一次
- 支持权重上下界设置

## 🔄 **向后兼容性**

### **兼容性层**

```python
# 原有代码无需修改
from alns_compatibility import adaptive_large_neighbourhood_search

result = adaptive_large_neighbourhood_search(meta_obj, initial_solution, True)
```

### **迁移路径**

```python
# 推荐的新方式
from alns_compatibility import migrate_alns_code

result = migrate_alns_code(meta_obj, initial_solution)
```

## 🧪 **测试覆盖**

### **测试组件**

- ✅ LNSConfig 配置测试
- ✅ OperatorConfig 操作符配置测试
- ✅ AcceptanceCriteria 接受准则测试
- ✅ RewardMechanisms 奖励机制测试
- ✅ LNSFramework 框架功能测试
- ✅ FactoryFunctions 工厂函数测试

### **运行测试**

```bash
cd tests
python test_lns_framework.py
```

## 📈 **优势对比**

### **原有ALNS vs 新框架**

| 特性 | 原有ALNS | 新LNS框架 |
|------|----------|-----------|
| **灵活性** | 固定配置 | 完全可配置 |
| **扩展性** | 难以扩展 | 易于扩展 |
| **复用性** | 特定于ALNS | 通用框架 |
| **监控性** | 有限统计 | 完整监控 |
| **测试性** | 难以测试 | 易于测试 |
| **维护性** | 代码耦合 | 模块化设计 |

## 🎨 **设计模式应用**

### **1. 策略模式 (Strategy Pattern)**

```python
# 不同的接受策略
acceptance_strategies = {
    AcceptanceStrategy.ALWAYS: AlwaysAccept(),
    AcceptanceStrategy.BETTER_ONLY: BetterOnlyAccept(),
    AcceptanceStrategy.SIMULATED_ANNEALING: SimulatedAnnealingAccept(),
    AcceptanceStrategy.PROBABILISTIC: ProbabilisticAccept(threshold=0.2)
}
```

### **2. 工厂模式 (Factory Pattern)**

```python
# 预配置的框架工厂
def create_alns_framework(config=None):
    # 创建ALNS框架
    
def create_simple_lns_framework(config=None):
    # 创建简单LNS框架
```

### **3. 模板方法模式 (Template Method)**

```python
class LNSFramework:
    def solve(self, initial_solution):
        # 模板方法，定义算法骨架
        for iteration in range(self.config.max_iterations):
            # 选择操作符
            # 应用操作符
            # 决定是否接受
            # 更新权重
```

### **4. 观察者模式 (Observer Pattern)**

```python
# 性能跟踪和统计
self.removal_performances.append(removal_perf)
self.insertion_performances.append(insertion_perf)
```

## 🔮 **未来扩展**

### **计划功能**

1. **并行执行**: 多进程/多线程支持
2. **混合策略**: 组合多种接受准则
3. **自适应参数**: 自动调整算法参数
4. **可视化**: 算法执行过程可视化
5. **分布式**: 支持分布式计算

### **扩展接口**

```python
# 自定义温度计算
def custom_temperature(self, solution):
    return custom_logic()

# 自定义权重更新
def custom_weight_update(self, operators, performances):
    return custom_update_logic()
```

## 📚 **文档结构**

```
docs/
├── lns_framework_guide.md      # 详细使用指南
├── lns_framework_summary.md    # 架构总结 (本文档)
└── README.md                   # 项目总览

examples/
├── lns_framework_example.py    # 使用示例
└── parameter_tuning_example.py # 参数调优示例

tests/
└── test_lns_framework.py      # 完整测试套件
```

## 🎉 **总结**

新的LNS框架成功实现了：

1. **架构重构**: 从硬编码的ALNS到通用的LNS框架
2. **功能增强**: 支持多种接受策略和奖励机制
3. **易于使用**: 提供预配置的框架和简单的API
4. **向后兼容**: 现有代码无需修改即可使用
5. **完全可扩展**: 支持自定义组件和策略
6. **质量保证**: 完整的测试覆盖和文档

这个框架为后续的算法研究和应用提供了坚实的基础，让开发者可以：

- **快速实验**不同的LNS变体
- **轻松比较**不同策略的效果
- **灵活配置**算法参数
- **无缝迁移**现有代码
- **持续扩展**新功能

**LNS框架现在是一个真正企业级的、可扩展的优化算法框架！** 🚀
