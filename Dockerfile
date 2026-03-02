# Use Python 3.12 to match `requires-python` in pyproject.toml
FROM python:3.12-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt /app/
COPY pyproject.toml setup.py /app/

# Install system build tools, upgrade pip, then install requirements
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential \
	&& pip install --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir -r requirements.txt \
	&& apt-get purge -y --auto-remove build-essential \
	&& rm -rf /var/lib/apt/lists/*

# Copy application source
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 5000

# Command to run the FastAPI app
CMD ["python3", "app.py"]
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]