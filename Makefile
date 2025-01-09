# Define variables
DOCKER_IMAGE_NAME = FloTorch
DOCKERFILE_PATH = Dockerfile
BUILD_DIR = .
PLATFORM ?= linux/amd64
HANDLER ?= retriever_handler.lambda_handler
HANDLER_FOLDER ?= handlers

# Define targets for the image
IMAGE_TAG = flotorch

# Build the Docker image
.PHONY: build
build:
	docker build --platform $(PLATFORM) --build-arg PLATFORM=$(PLATFORM) --build-arg HANDLER=$(HANDLER) --build-arg HANDLER_FOLDER=$(HANDLER_FOLDER) -t $(IMAGE_TAG) -f $(DOCKERFILE_PATH) $(BUILD_DIR)

# Clean up built image
.PHONY: clean
clean:
	docker rmi $(IMAGE_TAG) || true

# Push the built image to a container registry
.PHONY: push
push:
	docker push $(IMAGE_TAG)

# Build with a specific handler folder, platform, and handler
.PHONY: custom_build
custom_build:
	docker build --platform $(PLATFORM) --build-arg PLATFORM=$(PLATFORM) --build-arg HANDLER=$(HANDLER) --build-arg HANDLER_FOLDER=$(HANDLER_FOLDER) -t $(IMAGE_TAG) -f $(DOCKERFILE_PATH) $(BUILD_DIR)