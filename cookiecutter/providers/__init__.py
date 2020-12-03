"""Providers."""
import os

native_providers = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
    for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), f))
    and f != '__pycache__'
]
