FROM python:3.11-slim

# Set environment variables to prevent Python from buffering stdout and to ensure pip runs properly
ENV PYTHONUNBUFFERED=1 \
    VENV_PATH=/app/venv

# Copy application code to the container
COPY . /app

# Set the working directory
WORKDIR /app

# Check if the virtual environment exists; if not, create it and install dependencies
RUN if [ ! -d "$VENV_PATH" ]; then \
        python -m venv $VENV_PATH && \
        $VENV_PATH/bin/pip install --upgrade pip && \
        $VENV_PATH/bin/pip install -r requirements.txt; \
    else \
        echo "Reusing existing virtual environment at $VENV_PATH"; \
    fi

# Update PATH to use the virtual environment
ENV PATH="$VENV_PATH/bin:$PATH"

# Default command to run the application
CMD ["python", "app.py"]
