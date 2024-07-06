import warnings

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("genaiserver_wl_folder")
except PackageNotFoundError:
    warnings.warn("Could not determine version of genaiserver_wl_folder", stacklevel=1)
    __version__ = "unknown"
