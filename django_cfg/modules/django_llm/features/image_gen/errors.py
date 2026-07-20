"""Typed text-to-image transport and provider-result errors."""


class ImageGenerationError(RuntimeError):
    pass


class NoImageGeneratedError(ImageGenerationError):
    def __init__(self, message: str, *, model_text: str = "") -> None:
        super().__init__(message)
        self.model_text = model_text
