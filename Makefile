TAG=test.7

build:
	docker build . -t gymming:$(TAG)

run: build
	docker run -d -p 5000 gymming:$(TAG)