FROM python:3.8-alpine

USER root

RUN apk add --no-cache make git bash

# cryptography: https://cryptography.io/en/latest/installation/#alpine add g++ as it seems to be missing
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev 
RUN pip install --upgrade pip
#RUN pip install --only-binary ":all:" grpcio
RUN apk add --no-cache g++
#RUN pip install firebase-admin


# https://stackoverflow.com/a/57485724
RUN apk add --update --no-cache py3-numpy py3-scipy py3-pillow
ENV PYTHONPATH "$PYTHONPATH:/usr/lib/python3.7/site-packages"

# golang
RUN apk add --no-cache go

# aea installation
#ENV GOPROXY=direct
#RUN pip install --upgrade pip
RUN pip install --upgrade --force-reinstall aea[all]==1.1.0
RUN pip install aea-ledger-fetchai==1.1.0
RUN pip install aea-ledger-ethereum==1.1.0

# directories and aea cli config
COPY /docker-aea-config /home/.aea
WORKDIR /home/agents
COPY ./packages /home/agents/packages
#COPY /home/kud7fe/.aea/packages /home/agents/packages
#RUN mkdir /home/agents/packages
#RUN --mount=src=/home/kud7fe/.aea/packages,target=/home/agents/packages,type=cache

# aea build script
COPY /docker-build.sh /build.sh
RUN ["chmod", "+x", "/build.sh"]
RUN [ "/build.sh" ]

# fix of Error: AttributeError("'NoneType' object has no attribute 'extensions_by_name'")
RUN pip install --upgrade --force-reinstall protobuf==3.20.0

# optionally, specify any ports to expose here
EXPOSE 9001
EXPOSE 11001

# aea entrypoint script
COPY /docker-entrypoint.sh /entrypoint.sh
RUN ["chmod", "+x", "/entrypoint.sh"]
CMD [ "/entrypoint.sh" ]