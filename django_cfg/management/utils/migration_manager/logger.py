class MigrationLogger:
    def __init__(self, stdout=None, style=None, logger=None):
        self.stdout = stdout
        self.style = style
        self.logger = logger

    def info(self, message: str):
        if self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.info(message)

    def success(self, message: str):
        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str):
        if self.stdout and self.style:
            self.stdout.write(self.style.WARNING(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str):
        if self.stdout and self.style:
            self.stdout.write(self.style.ERROR(message))
        elif self.stdout:
            self.stdout.write(message)
        if self.logger:
            self.logger.error(message)

    def raise_error(self, message: str):
        self.error(f"❌ {message}")
        raise Exception(message)
