FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    git \
    python3 \
    sqlite3 \
    python3-venv \
    python3-pip \
    openssh-server \
    sudo \
    && apt-get clean

RUN mkdir /var/run/sshd


RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

WORKDIR /root/
COPY . .
RUN chmod +x script.sh
RUN ./script.sh
RUN rm -f script.sh
WORKDIR /root/backend/
RUN python3 -m venv backend_venv && \
    ./backend_venv/bin/pip install --upgrade pip && \
    ./backend_venv/bin/pip install -r requirements.txt

EXPOSE 80 22

CMD service ssh start && ./backend_venv/bin/python3 main.py

