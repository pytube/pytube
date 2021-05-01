from typing import Any, Callable, Optional


class Monostate:
    def __init__(
        self,
        on_progress: Optional[Callable[[Any, bytes, int], None]],
        on_complete: Optional[Callable[[Any, Optional[str]], None]],
        title: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.title = title
        self.duration = duration
