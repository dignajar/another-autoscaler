FROM python:3.9.9-alpine3.14

ENV PYTHONUNBUFFERED=1

COPY files/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt --no-cache-dir

# Run as non-root
ENV USER autoscaler
ENV UID 10001
ENV GROUP autoscaler
ENV GID 10001
ENV HOME /home/$USER
RUN addgroup -g $GID -S $GROUP && adduser -u $UID -S $USER -G $GROUP

# Copy app
COPY --chown=$UID:$GID ./files/ $HOME/

USER $UID:$GID
WORKDIR $HOME
CMD ["python3", "-u", "main.py"]