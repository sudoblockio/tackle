"""Providers."""
import os

file_path = os.path.dirname(os.path.abspath(__file__))

native_providers = [
    os.path.join(file_path, f)
    for f in os.listdir(file_path)
    if os.path.isdir(os.path.join(file_path, f))
    and f != '__pycache__'
]

if __name__ == '__main__':
    print(native_providers)
