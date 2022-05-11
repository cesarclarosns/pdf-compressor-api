# Note: The order of these instructions is important because Docker implements
# a caching strategy to build the containers.

# The base image for the container.
FROM python:3.10-slim-bullseye
# Debian bullseye

# Define working directory.
WORKDIR /usr/src

# Keep Python from generating .pyc files in the container.
ENV PYTHONDONTWRITEBYTECODE=1
# Turn off buffering for easier container logging.
ENV PYTHONUNBUFFERED=1

# Install required modules
COPY requirements.txt ./
RUN apt-get update && \
    apt-get install -y ghostscript && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists && \
    pip install -r requirements.txt

# Copy the rest of the files
COPY . .