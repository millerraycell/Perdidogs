# set base image (host OS)
FROM python:latest

# set the working directory in the container
WORKDIR /backend

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./src/ /backend/src/ 

# command to run on container start
CMD [ "python3", "src/core.py" ]
