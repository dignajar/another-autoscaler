FROM python:3.9.5-alpine3.13

ENV PYTHONUNBUFFERED=0

COPY files/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --no-cache-dir

# Run as non-root
ENV USER autoscaler
ENV UID 10001
ENV GROUP autoscaler
ENV GID 10001
ENV HOME /home/$USER
RUN addgroup -g $GID -S $GROUP && adduser -u $UID -S $USER -G $GROUP

# Python code
COPY files/* $HOME/
RUN chown -R $USER:$GROUP $HOME

USER $UID:$GID
WORKDIR $HOME
CMD ["python3", "-u", "main.py"]