# TC PDWTW Java Implementation

This is a Java port of the Python TC_PDWTW (Pickup and Delivery Problem with Time Windows) implementation.

## Project Structure

```
java-version-claude/
├── src/main/java/com/tc/pdwtw/
│   ├── algorithm/          # Algorithm implementations (ALNS, Two-Stage, etc.)
│   ├── benchmark/          # Benchmark readers and data processing
│   ├── example/            # Example usage and test classes
│   ├── model/              # Core data model classes
│   └── util/               # Utility classes
├── src/test/java/          # Unit tests
├── benchmark/              # Benchmark data files
└── pom.xml                 # Maven build configuration
```

## Requirements

- Java 11 or higher
- Maven 3.6 or higher

## Building the Project

```bash
mvn clean compile
```

## Running Tests

```bash
mvn test
```

## Running Examples

### Two-stage algorithm demo:
```bash
mvn exec:java -Dexec.mainClass="com.tc.pdwtw.example.TwoStageExample"
```

### Using the provided script:
```bash
./run-demo.sh
```

## Core Classes

### Model Classes
- `Node`: Represents a location with coordinates and time windows
- `Request`: Represents a pickup and delivery request
- `Vehicle`: Represents a vehicle with capacity and velocity
- `Path`: Represents a vehicle's route through nodes with insertion/removal operations
- `Meta`: Contains all problem data and configuration
- `PDWTWSolution`: Complete solution representation with cost calculation

### Algorithm Classes
- `ALNS`: Adaptive Large Neighborhood Search implementation
- `TwoStage`: Two-stage algorithm for vehicle minimization and optimization
- `InsertionOperators`: Best insertion, greedy insertion, and regret-based operators
- `RemovalOperators`: Shaw, random, and worst removal operators

### Utility Classes
- `Parameters`: Algorithm parameters with validation and tuning capabilities
- `FileReader`: Abstract base for reading problem data
- `BenchmarkReader`: Abstract base for benchmark data processing
- `LiLimBenchmarkReader`: Reader for Li & Lim PDPTW benchmark files

## Features Implemented

✅ Core data model (Node, Request, Vehicle, Path, Meta, Solution)
✅ Parameter management with validation and ranges
✅ Complete path operations (insertion, removal, cost calculation)
✅ Solution management and objective calculation
✅ **ALNS algorithm implementation** with adaptive weights and operators
✅ **Removal operators** (Shaw removal, Random removal, Worst removal)
✅ **Insertion operators** (Best insertion, Greedy insertion, Regret-based insertion)
✅ **Two-stage algorithm** for vehicle minimization and cost optimization
✅ **Li & Lim benchmark file readers** for standard PDPTW datasets
✅ Complete path removal and reconstruction logic
✅ Simulated annealing acceptance criteria
✅ Maven build configuration
✅ Working example applications (TwoStageExample)

## Features Not Yet Implemented

❌ Additional benchmark format readers (Solomon, Cordeau, etc.)
❌ Advanced neighborhood operators
❌ Parallel processing capabilities
❌ Solution visualization tools
❌ Performance benchmarking suite

## Converting from Python

This Java implementation maintains the same core algorithms and data structures as the Python version, with adaptations for Java's type system and conventions:

- Python dictionaries → Java HashMap/Map
- Python sets → Java HashSet/Set  
- Python lists → Java ArrayList/List
- Python tuples → Java custom classes or arrays
- Python properties → Java getter/setter methods
- Python duck typing → Java interfaces and inheritance

## License

MIT License - see the original Python implementation for full license text.

## Contributing

This is a direct port of the Python implementation. For algorithm improvements or bug fixes, please consider contributing to both versions.