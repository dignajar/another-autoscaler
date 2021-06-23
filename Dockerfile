FROM python:3.9.5-alpine3.13

ENV PYTHONUNBUFFERED=0

#RUN apk --no-cache add build-base openldap-dev libffi-dev
COPY files/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --no-cache-dir

# Run as non-root
ENV USER scheduler
ENV UID 10001
ENV GROUP scheduler
ENV GID 10001
ENV HOME /home/$USER
RUN addgroup -g $GID -S $GROUP && adduser -u $UID -S $USER -G $GROUP

# Python code
COPY files/* $HOME/
RUN chown -R $USER:$GROUP $HOME

#EXPOSE 9000
USER $UID:$GID
WORKDIR $HOME
CMD ["python3", "-u", "main.py"]