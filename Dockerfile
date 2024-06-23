# Build stage
FROM python:3.10-slim as builder

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Make
RUN apt-get update && apt-get install -y build-essential make

# Install Poetry
RUN pip install poetry

# Copy only the necessary files for building
COPY pyproject.toml poetry.lock Makefile ./

# Copy the rest of the application code
COPY . .

# Build the distribution package
RUN make dist

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Copy the built dist from the builder stage
COPY --from=builder /app/dist/*.whl ./

# Install the wheel package
RUN pip install *.whl && rm *.whl

# Set the default command to run the subgenix tool
CMD ["subgenix"]
