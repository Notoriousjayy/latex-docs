package edu.ci;
public final class Calculator {
    private Calculator() {}
    public static long add(long a, long b) { return Math.addExact(a, b); }
    public static long multiply(long a, long b) { return Math.multiplyExact(a, b); }
}
