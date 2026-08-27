"""TRMNL Liquid compatibility layer for Python."""

from .__about__ import __version__
from .environment import Environment, render

__all__ = ["Environment", "__version__", "render"]
