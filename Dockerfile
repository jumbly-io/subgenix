FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Install Poetry
RUN pip install poetry

# Copy only the necessary files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Install dependencies for development
RUN poetry install

# Copy the rest of the application code
COPY . .

# Install pre-commit hooks and run make develop
RUN make develop

# Build the distribution package
RUN make build

# Install the distribution package
RUN make install

CMD ["python", "src/subgenix.py"]
