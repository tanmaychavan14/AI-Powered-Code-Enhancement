import pytest
import inspect
import sys
from pathlib import Path

# Add the source directory to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from imgSteg import *
except ImportError as e:
    print(f"Import error: {e}")
    # Try alternative import methods
    import importlib.util
    spec = importlib.util.spec_from_file_location("imgSteg", Path(__file__).parent.parent / "imgSteg.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    globals().update({name: getattr(module, name) for name in dir(module) if not name.startswith('_')})


# Tests for add function
def test_add_exists():
    """Test that add function exists"""
    assert callable(add), f"add should be callable"

def test_add_addition():
    """Test add performs addition correctly"""
    if len(inspect.signature(add).parameters) >= 2:
        result = add(5, 3)
        assert isinstance(result, (int, float)), "Should return a number"
        assert result == 8, "5 + 3 should equal 8"
    else:
        # Single parameter function
        result = add(5)
        assert result is not None

def test_add_negative_numbers():
    """Test add with negative numbers"""
    if len(inspect.signature(add).parameters) >= 2:
        result = add(-2, -3)
        assert isinstance(result, (int, float))
        assert result == -5, "-2 + -3 should equal -5"

def test_add_zero():
    """Test add with zero"""
    if len(inspect.signature(add).parameters) >= 2:
        result = add(0, 5)
        assert result == 5, "0 + 5 should equal 5"


# Tests for subtract function
def test_subtract_exists():
    """Test that subtract function exists"""
    assert callable(subtract), f"subtract should be callable"

def test_subtract_subtraction():
    """Test subtract performs subtraction correctly"""
    if len(inspect.signature(subtract).parameters) >= 2:
        result = subtract(10, 3)
        assert isinstance(result, (int, float))
        assert result == 7, "10 - 3 should equal 7"

def test_subtract_negative_result():
    """Test subtract with negative result"""
    if len(inspect.signature(subtract).parameters) >= 2:
        result = subtract(3, 10)
        assert result == -7, "3 - 10 should equal -7"


# Tests for multiply function
def test_multiply_exists():
    """Test that multiply function exists"""
    assert callable(multiply), f"multiply should be callable"

def test_multiply_multiplication():
    """Test multiply performs multiplication correctly"""
    if len(inspect.signature(multiply).parameters) >= 2:
        result = multiply(4, 3)
        assert isinstance(result, (int, float))
        assert result == 12, "4 * 3 should equal 12"

def test_multiply_by_zero():
    """Test multiply multiplication by zero"""
    if len(inspect.signature(multiply).parameters) >= 2:
        result = multiply(5, 0)
        assert result == 0, "5 * 0 should equal 0"


# Tests for divide function
def test_divide_exists():
    """Test that divide function exists"""
    assert callable(divide), f"divide should be callable"

def test_divide_division():
    """Test divide performs division correctly"""
    if len(inspect.signature(divide).parameters) >= 2:
        result = divide(10, 2)
        assert isinstance(result, (int, float))
        assert result == 5, "10 / 2 should equal 5"

def test_divide_division_by_zero():
    """Test divide handles division by zero"""
    if len(inspect.signature(divide).parameters) >= 2:
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

def test_divide_float_division():
    """Test divide with float division"""
    if len(inspect.signature(divide).parameters) >= 2:
        result = divide(7, 2)
        assert result == 3.5, "7 / 2 should equal 3.5"

