# Use a minimal Python image to keep the container lightweight
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy the server script into the image
COPY server.py .

# Expose the port our server listens on
EXPOSE 8080

# PID 1 will be the Python interpreter running server.py directly.
# We use CMD (not ENTRYPOINT + shell) so Python is PID 1, not /bin/sh.
CMD ["python3", "-u", "server.py"]
