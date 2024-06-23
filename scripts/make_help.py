import re
from pathlib import Path

# Regular expression to match the comment lines and target lines
comment_pattern = re.compile(r"^## (.*)$")
target_pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_-]*):")

commands = []

for file in Path("./Makefiles").glob("*.mk"):
    with file.open() as f:
        lines = f.readlines()
        comment = None
        for line in lines:
            line = line.rstrip()
            comment_match = comment_pattern.match(line)
            if comment_match:
                comment = comment_match.group(1)
            else:
                target_match = target_pattern.match(line)
                if target_match and comment:
                    target = target_match.group(1)
                    commands.append(f"\033[36m{target:<20}\033[0m {comment}")
                    comment = None  # Reset comment after it's been used

# Sort the commands alphabetically
commands.sort()

# Print all the matched commands
for command in commands:
    print(command)
