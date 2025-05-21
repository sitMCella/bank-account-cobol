FROM alpine:3.21 AS builder

# Dependencies
RUN apk --no-cache add wget xz make vim nano sudo build-base ncurses-dev db-dev db gmp-dev

ARG COBOL_VERSION=3.2
ARG COBOL_VERSION_REV=3.2

# Cobol
# https://github.com/fink/fink-mirrors/blob/master/sourceforge
#RUN wget --no-check-certificate https://downloads.sourceforge.net/project/gnucobol/gnucobol/$COBOL_VERSION/gnucobol-$COBOL_VERSION_REV.tar.xz

COPY backend/gnucobol-$COBOL_VERSION_REV.tar.xz .

RUN xz -d gnucobol-$COBOL_VERSION_REV.tar.xz \
 && tar xvf gnucobol-$COBOL_VERSION_REV.tar \
 && cd gnucobol-$COBOL_VERSION_REV \
 && ./configure \
 && make install \
 && cd .. \
 && rm -rf gnucobol-*

# Create new user `cobol` and disable 
# password and gecos for later
# --gecos explained well here:
# https://askubuntu.com/a/1195288/635348
RUN adduser \
  --disabled-password \
  --home /app \
  --gecos '' cobol \
  && chown -R cobol /app

# Ensure sudo group users are not 
# asked for a password when using 
# sudo command by ammending sudoers file
RUN echo '%cobol ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && \
    echo '%cobol ALL=(ALL) ALL' > /etc/sudoers.d/cobol

# now we can set USER to the user we just created
USER cobol

WORKDIR /app

COPY backend/cobol/*.cob /app

COPY backend/cobol/makefile /app

RUN make all


FROM python:3.14-rc-alpine

# Dependencies
RUN apk --no-cache add wget xz make vim nano sudo build-base ncurses-dev db-dev db gmp-dev db-utils

ARG COBOL_VERSION=3.2
ARG COBOL_VERSION_REV=3.2

# Cobol
# https://github.com/fink/fink-mirrors/blob/master/sourceforge
#RUN wget --no-check-certificate https://downloads.sourceforge.net/project/gnucobol/gnucobol/$COBOL_VERSION/gnucobol-$COBOL_VERSION_REV.tar.xz

COPY backend/gnucobol-$COBOL_VERSION_REV.tar.xz .

RUN xz -d gnucobol-$COBOL_VERSION_REV.tar.xz \
 && tar xvf gnucobol-$COBOL_VERSION_REV.tar \
 && cd gnucobol-$COBOL_VERSION_REV \
 && ./configure \
 && make install \
 && cd .. \
 && rm -rf gnucobol-*

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/app
COPY backend/requirements.txt /opt/app
RUN mkdir -p /opt/app/storage
WORKDIR /opt/app

RUN pip install -r requirements.txt

COPY --from=builder /app/*.so /opt/app

COPY backend/cobol.py /opt/app
COPY backend/main.py /opt/app

EXPOSE 8081

CMD ["python", "main.py"]
