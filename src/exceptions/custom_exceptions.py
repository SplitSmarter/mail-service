class MailError(Exception):

    def __init__(self, message: str = "Failed to send email via all providers.", errors: dict = None):
        self.message = message
        self.errors = errors or {}
        super().__init__(self.message)

    def __str__(self):
        provider_errors = "\n".join(
            f"{provider}: {error}" for provider, error in self.errors.items()
        )
        return f"{self.message}\nDetails:\n{provider_errors}"
