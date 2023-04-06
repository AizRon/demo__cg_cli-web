FROM nginx/unit:1.28.0-python3.10

EXPOSE 5000

ENV TZ=Europe/Moscow
COPY ./communigate_cli-web/requirements.txt /config/requirements.txt

RUN apt update && apt install -y python3-pip tzdata \
	&& pip3 install -r /config/requirements.txt \
	&& apt remove -y python3-pip \
	&& apt autoremove --purge -y \
	&& rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list
