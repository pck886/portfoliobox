import warnings

warnings.warn("include('portfolio.urls') is deprecated; use include('portfolio.backends.default.urls') instead.",
              DeprecationWarning)

from .backends.default.urls import * # NOQA