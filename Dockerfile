FROM python:3.13.0-alpine
LABEL maintainer="sanpeter992000@gmail.com"
# Ensures Python output is sent straight to the terminal (without buffering),
# allowing real-time logging and easier debugging.
ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
COPY ./app /app
# Sets the working directory inside the container to /app.
# All subsequent commands will be run from this directory.
WORKDIR /app
# Informs Docker that the container listens on port 8000.
# This is used for documentation purposes and to help with port binding.
EXPOSE 8000
# Combining multiple commands in a single RUN instruction reduces the number of layers in the image,
# which can lead to a smaller image size and improved build performance.
# Create a virtual environment in /venv
RUN python -m venv /venv && \
    # Upgrade pip within the virtual environment
    /venv/bin/pip install --upgrade pip && \
    # Install the dependencies from requirements.txt
    /venv/bin/pip install -r /requirements.txt && \
    # Add a new user named 'app' without a password and without creating a home directory
    adduser --disabled-password --no-create-home app
# Update the PATH environment variable to prioritize the virtual environment's bin directory.
# This ensures that Python and pip commands use the versions installed in the virtual environment by default.
ENV PATH="/venv/bin:$PATH"
# Switches the current user to 'app'
# to ensure that subsequent commands are run with non-root privileges, which enhances security by limiting the actions
# that can be performed by the processes within the container.
USER app