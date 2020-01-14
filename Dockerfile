# https://www.howtoforge.com/tutorial/how-to-create-docker-images-with-dockerfile/

#Download base image ubuntu 16.04
FROM ubuntu:18.04

# Update Ubuntu Software repository
RUN apt-get update

# Python3
RUN apt-get -y install python3