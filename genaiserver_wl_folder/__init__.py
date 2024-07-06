import importlib.metadata
import warnings

try:
    __version__ = importlib.metadata.version("genaiserver_wl_folder")
except importlib.metadata.PackageNotFoundError as e:
    warnings.warn("Could not determine version of genaiserver_wl_folder", stacklevel=1)
    __version__ = "unknown"
