#!/bin/bash

# TC PDWTW Java Demo Runner
# Compiles and runs the Java implementation

echo "TC PDWTW Java Implementation Demo"
echo "================================="

# Clean previous compilation
rm -rf com/

# Compile all Java files
echo "Compiling Java source files..."
javac -cp . -d . src/main/java/com/tc/pdwtw/*/*.java

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
    echo ""
    echo "Running SimpleTest example..."
    echo "-----------------------------"
    java -cp . com.tc.pdwtw.example.TwoStageExample
else
    echo "Compilation failed!"
    exit 1
fi