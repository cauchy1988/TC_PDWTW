package com.tc.pdwtw.model;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Abstract base class for solution representations
 */
public abstract class Solution {
    protected Meta metaObj;
    
    public Solution(Meta metaObj) {
        this.metaObj = metaObj;
    }
    
    public Meta getMetaObj() {
        return metaObj;
    }
}