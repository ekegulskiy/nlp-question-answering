# https://www.howtoforge.com/tutorial/how-to-create-docker-images-with-dockerfile/

#Download base image ubuntu 16.04
FROM ubuntu:18.04

# Update Ubuntu Software repository
RUN apt-get update

# Python3, git, java (needed for nltk)
RUN apt-get -y install python3 python3-pip git default-jdk

# nltk
RUN pip3 install --user -U nltk
RUN python3 -m nltk.downloader stopwords punkt

# other dependencies
RUN pip3 install word2number gitpython progressbar

# get latest nlp-question-answering sources
WORKDIR /home
RUN git clone https://github.com/ekegulskiy/nlp-question-answering
WORKDIR /home/nlp-question-answering
# run setup script (to download stanford POS and NER models)
RUN python3 setup_env.py