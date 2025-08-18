package com.tc.pdwtw.model;

import java.util.Set;

/**
 * MIT License
 * 
 * Copyright (c) 2024 cauchy1988
 * 
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
public class Request {
    private final int identity;
    private final int pickNodeId;
    private final int deliveryNodeId;
    private final double requireCapacity;
    private final Set<Integer> vehicleSet;

    public Request(int identity, int pickupNodeId, int deliveryNodeId, 
                   double requireCapacity, Set<Integer> vehicleSet) {
        this.identity = identity;
        this.pickNodeId = pickupNodeId;
        this.deliveryNodeId = deliveryNodeId;
        this.requireCapacity = requireCapacity;
        this.vehicleSet = vehicleSet;
    }

    public int getIdentity() {
        return identity;
    }

    public int getPickNodeId() {
        return pickNodeId;
    }

    public int getDeliveryNodeId() {
        return deliveryNodeId;
    }

    public double getRequireCapacity() {
        return requireCapacity;
    }

    public Set<Integer> getVehicleSet() {
        return vehicleSet;
    }
}