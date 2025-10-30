FROM python:3.13

# Create a custom user with UID 1234 and GID 1234
RUN groupadd -g 0505 awg && \
    useradd -m -u 0605 -g awg workflow
USER workflow

WORKDIR /opt/workflow
COPY requirements.txt .
COPY plot.py .

RUN pip install --no-cache-dir -r ./requirements.txt
ENTRYPOINT python3 ./plot.py