# docker build -t execution_engine -f Dockerfile .
# docker run -p 3000:3000 execution_engine


FROM python:3.12

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update -y
RUN apt -y install build-essential git gcc make libtool libltdl-dev automake autoconf bison byacc flex libpango1.0-dev python3
RUN apt install python3-pip -y
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rm -rf requirements.txt

RUN git clone https://gitlab.com/graphviz/graphviz/
WORKDIR /graphviz
RUN ./autogen.sh \
	&& ./configure \
    && make \
	&& make -j6 install
RUN dot -c

WORKDIR /
COPY ./main.py ./swap-it-execution-engine/main.py
COPY ./control_interface ./swap-it-execution-engine/control_interface
COPY ./dispatcher ./swap-it-execution-engine/dispatcher
COPY ./execution_engine_logic ./swap-it-execution-engine/execution_engine_logic
COPY ./PFDL_Examples ./swap-it-execution-engine/PFDL_Examples
WORKDIR /swap-it-execution-engine

EXPOSE 3000
CMD ["python3", "main.py", "opc.tcp://0.0.0.0:3000", "./PFDL_Examples/advanced.pfdl", "dashboard_host_address=http://host.docker.internal:8080", "log_info=True", "device_registry_url=opc.tcp://host.docker.internal:8000", "custom_url=opc.tcp://host.docker.internal:", "number_default_clients=5"]
