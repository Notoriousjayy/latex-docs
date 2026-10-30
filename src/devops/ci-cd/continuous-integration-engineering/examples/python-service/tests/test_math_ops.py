import pytest
from ci_engineering import safe_divide, running_total

def test_divide():
    assert safe_divide(9, 3) == 3

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        safe_divide(5, 0)

def test_running_total():
    assert running_total([1, -2, 4]) == 3
