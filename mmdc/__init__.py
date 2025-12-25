from .__about__ import __version__

# Export the main converter class
from .mmdc import MermaidConverter

__all__ = ['__version__', 'MermaidConverter']
