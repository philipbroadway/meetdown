# Use the official Python image as the base image
FROM python:3.9

# Set the working directory to /meetdown
WORKDIR /meetdown

# Copy the entire project into the container at /meetdown
COPY . /meetdown

RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
