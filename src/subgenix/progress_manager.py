import sys
from typing import Optional
from tqdm import tqdm  # type: ignore


class ProgressManager:
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.current_task: Optional[tqdm] = None

    def start_task(self, description: str, total: Optional[int] = None):
        if self.show_progress:
            self.current_task = tqdm(
                total=total,
                desc=description,
                unit="step",
                file=sys.stdout,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}" if total is not None else "{l_bar}{bar}",
                disable=total is None,
            )

    def update_progress(self, steps: int = 1):
        if self.show_progress and self.current_task:
            self.current_task.update(steps)

    def set_total(self, total: int):
        if self.show_progress and self.current_task:
            self.current_task.total = total
            self.current_task.refresh()

    def complete_task(self, description: Optional[str] = None):
        if self.show_progress and self.current_task:
            if description:
                self.current_task.set_description(description)
            self.current_task.close()
            self.current_task = None

    def fail_task(self, description: str):
        if self.show_progress and self.current_task:
            self.current_task.set_description(f"Failed: {description}")
            self.current_task.close()
            self.current_task = None
        print(f"Task failed: {description}", file=sys.stderr)

    def print_message(self, message: str):
        if self.show_progress:
            if self.current_task:
                tqdm.write(message)
            else:
                print(message)
