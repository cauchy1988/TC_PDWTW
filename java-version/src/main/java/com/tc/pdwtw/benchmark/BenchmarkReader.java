package com.tc.pdwtw.benchmark;

import com.tc.pdwtw.model.Meta;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Abstract base class for benchmark readers that create Meta objects from benchmark data
 */
public abstract class BenchmarkReader {
    
    public BenchmarkReader() {
    }
    
    /**
     * Get a Meta object populated with benchmark data
     * 
     * @return Meta object containing the problem instance data
     */
    public abstract Meta getMetaObj();
}