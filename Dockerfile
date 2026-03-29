FROM python:3.10-slim

WORKDIR /app

# Install both Pillow and Flask
RUN pip install --no-cache-dir Pillow Flask

# Expose port 5000 for the web server
EXPOSE 5000

# Tell Docker to run the new web app
CMD ["python", "web_app.py"]