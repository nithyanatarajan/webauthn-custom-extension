class ExtensionValidationError(Exception):
    """Raised when custom extension server validation fails."""

    def __init__(self, message: str, *, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause
