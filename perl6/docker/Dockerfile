FROM rakudo-star:latest
RUN apt-get update \
	&& apt-get dist-upgrade -y \
	&& panda update \
	&& panda install JSON::Pretty YAMLish Data::Dump \
	&& apt-get clean -y \
	&& rm -rf /var/lib/apt/lists/*
