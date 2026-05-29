"""Exception classes used by pyThermoDB.

The package should raise built-in exceptions for simple Python contract
violations, such as ``TypeError`` for a wrong argument type. Use these
exceptions for pyThermoDB domain failures so callers can catch package errors
without catching every possible Python exception.
"""

from __future__ import annotations

from typing import Any, Mapping


class PyThermoDBError(Exception):
    """Base exception for all pyThermoDB-specific errors."""

    default_message = "pyThermoDB error"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | int | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.code = code
        self.context = dict(context or {})
        super().__init__(self.message)

    def __str__(self) -> str:
        message = self.message
        if self.code is not None:
            message = f"[{self.code}] {message}"
        if self.context:
            details = ", ".join(
                f"{key}={value!r}" for key, value in self.context.items()
            )
            message = f"{message} ({details})"
        return message


class ConfigurationError(PyThermoDBError):
    """Invalid package, reference, or user configuration."""

    default_message = "Invalid configuration"


class ReferenceError(PyThermoDBError):
    """Reference loading, parsing, or lookup failed."""

    default_message = "Reference operation failed"


class ReferenceNotFoundError(ReferenceError, LookupError):
    """Requested databook, table, component, property, or symbol was not found."""

    default_message = "Reference item was not found"


class DataValidationError(PyThermoDBError, ValueError):
    """Input data exists but is malformed or invalid for pyThermoDB."""

    default_message = "Data validation failed"


class ThermoDBBuildError(PyThermoDBError):
    """Building a thermodb object failed."""

    default_message = "ThermoDB build failed"


class ThermoDBLoadError(PyThermoDBError):
    """Loading a saved thermodb object failed."""

    default_message = "ThermoDB load failed"


class EquationError(PyThermoDBError):
    """Equation parsing, normalization, formatting, or evaluation failed."""

    default_message = "Equation operation failed"


class SymbolError(PyThermoDBError):
    """Symbol loading, lookup, or validation failed."""

    default_message = "Symbol operation failed"


class BuilderError(PyThermoDBError):
    """Builder operation failed."""

    default_message = "Builder operation failed"


class ExportError(PyThermoDBError):
    """Exporting or serialization failed."""

    default_message = "Export operation failed"


class errHandler(PyThermoDBError):
    """Backward-compatible alias for the previous generic error class."""


class errGeneral(PyThermoDBError):
    """Backward-compatible generic error with the old ``errCode`` API."""

    def __init__(self, errCode: str | int, errMessage: str) -> None:
        self.errCode = errCode
        self.errMessage = errMessage
        super().__init__(errMessage, code=errCode)

    def errType(self) -> str:
        return self.__class__.__name__


__all__ = [
    "PyThermoDBError",
    "ConfigurationError",
    "ReferenceError",
    "ReferenceNotFoundError",
    "DataValidationError",
    "ThermoDBBuildError",
    "ThermoDBLoadError",
    "EquationError",
    "SymbolError",
    "BuilderError",
    "ExportError",
    "errHandler",
    "errGeneral",
]
