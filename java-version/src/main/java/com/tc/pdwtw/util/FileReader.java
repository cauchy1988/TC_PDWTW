package com.tc.pdwtw.util;

import com.tc.pdwtw.model.Meta;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Abstract base class for file readers that load problem data into Meta objects
 */
public abstract class FileReader {
    
    public FileReader() {
    }
    
    /**
     * Read problem data from a directory into the provided Meta object
     * 
     * @param directoryPath Path to the directory containing problem files
     * @param metaObj Meta object to populate with data
     */
    public abstract void readFromDirectory(String directoryPath, Meta metaObj);
}