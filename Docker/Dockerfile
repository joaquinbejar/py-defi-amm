# Base image
FROM python:3.12-slim-bookworm AS builder

# Install additional packages
RUN apt-get -y update && \
	apt-get -y install \
		python3-dev \
		gcc \
		krb5-multidev \
		git \
        make \
    && apt-get clean
	

# Set current dir
WORKDIR /app

# Copy codebase
ADD . .

RUN make install-dep

RUN make create-executable

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=builder /app/dist/main /app

RUN chmod +x /app/main

RUN chown -R 1001 /app
USER 1001

CMD ["/app/main"]