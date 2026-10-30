package edu.ci;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class CalculatorTest {
    @Test void addition() { assertEquals(5, Calculator.add(2, 3)); }
    @Test void negativeMultiply() { assertEquals(-12, Calculator.multiply(3, -4)); }
    @Test void overflowFails() { assertThrows(ArithmeticException.class, () -> Calculator.add(Long.MAX_VALUE, 1)); }
}
