import pytest
import sys
import os

# Add the parent directory to the path so we can import the utils modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_processor import process_text
from utils.image_generator import get_anchor_position

def test_text_processing_uppercase():
    """Test that text is properly transformed to uppercase"""
    settings = {
        "advanced": {
            "text_transform": "uppercase"
        }
    }
    
    text = "Hello World"
    result = process_text(text, settings)
    assert result == "HELLO WORLD"

def test_text_processing_lowercase():
    """Test that text is properly transformed to lowercase"""
    settings = {
        "advanced": {
            "text_transform": "lowercase"
        }
    }
    
    text = "Hello World"
    result = process_text(text, settings)
    assert result == "hello world"

def test_text_processing_capitalize():
    """Test that text is properly capitalized"""
    settings = {
        "advanced": {
            "text_transform": "capitalize"
        }
    }
    
    text = "hello world"
    result = process_text(text, settings)
    assert result == "Hello World"

def test_text_processing_none():
    """Test that text is not transformed when transform is none"""
    settings = {
        "advanced": {
            "text_transform": None
        }
    }
    
    text = "Hello World"
    result = process_text(text, settings)
    assert result == "Hello World"

def test_anchor_position():
    """Test that the correct anchor positions are returned"""
    assert get_anchor_position("left") == "lm"
    assert get_anchor_position("center") == "mm"
    assert get_anchor_position("right") == "rm"