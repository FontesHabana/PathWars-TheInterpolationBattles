import sys
import os

# Add src to the path so tests can import from it
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest

# Session-scoped pygame initialization
@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame once for all tests."""
    import pygame
    pygame.init()
    yield
    pygame.quit()
