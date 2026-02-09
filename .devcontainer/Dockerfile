FROM mcr.microsoft.com/devcontainers/python:3.11

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        postgresql-client \
        sqlite3 \
        curl \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the default shell
SHELL ["/bin/bash", "-c"]

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/workspaces/src

# Create workspace directory
WORKDIR /workspaces

# Copy requirements files
COPY requirements/requirements.txt /tmp/requirements.txt
COPY dev_requirements.txt /tmp/dev_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/dev_requirements.txt

# Create a non-root user for development
RUN useradd -m -s /bin/bash vscode \
    && chown -R vscode:vscode /workspaces

USER vscode

# Set the working directory
WORKDIR /workspaces

# Default command
CMD ["sleep", "infinity"]
