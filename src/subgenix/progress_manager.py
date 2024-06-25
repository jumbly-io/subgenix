import sys
from typing import Optional
from tqdm import tqdm  # type: ignore


class ProgressManager:
    def __init__(self, show_progress: bool = True):
        self.show_progress = show_progress
        self.current_task: Optional[tqdm] = None

    def start_task(self, description: str, total: Optional[int] = None):
        if self.show_progress and total is not None:
            self.current_task = tqdm(
                total=total,
                desc=description,
                unit="step",
                file=sys.stdout,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            )
        else:
            print(f"Starting task: {description}")

    def update_progress(self, steps: int = 1):
        if self.show_progress and self.current_task:
            self.current_task.update(steps)

    def complete_task(self, description: str):
        if self.current_task:
            self.current_task.close()
        print(f"Completed task: {description}")

    def fail_task(self, description: str):
        if self.current_task:
            self.current_task.close()
        print(f"Failed task: {description}", file=sys.stderr)

    def print_message(self, message: str):
        if self.show_progress:
            if self.current_task:
                tqdm.write(message)
            else:
                print(message)
