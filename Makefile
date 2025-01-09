# Define variables
DOCKER_IMAGE_NAME = flotorch
DOCKERFILE_PATH = make.Dockerfile
BUILD_DIR = .
PLATFORM ?= linux/amd64
SERVICE ?=
VERSION ?= latest  # Default version tag

# List of all possible services
SERVICES = retriever indexer evaluator

# Define a map of services to handlers
HANDLER_MAP = retriever:handlers/retriever_handler \
              indexer:handlers/indexing_handler \
              evaluator:handlers/evaluation_handler

# Define the image tag based on the service and version
IMAGE_TAG = $(DOCKER_IMAGE_NAME):$(SERVICE)-$(VERSION)

# Extract handler for the selected service
SERVICE_HANDLER = $(shell echo $(HANDLER_MAP) | grep -o "\b$(SERVICE):[^\ ]*" | cut -d: -f2)

# Build the Docker image for all services or a specific service
.PHONY: build
build:
ifeq ($(SERVICE),)
	# If SERVICE is empty, loop through all services and build
	$(foreach service,$(SERVICES),$(MAKE) build_service SERVICE=$(service) VERSION=$(VERSION);)
else
	# Otherwise, build the specified service
	$(MAKE) build_service SERVICE=$(SERVICE) VERSION=$(VERSION)
endif

# Build the Docker image for a specific service
.PHONY: build_service
build_service:
	docker build --platform $(PLATFORM) \
		--build-arg PLATFORM=$(PLATFORM) \
		--build-arg HANDLER=$(SERVICE_HANDLER) \
		--build-arg HANDLER_FOLDER=$(SERVICE) \
		--build-arg SERVICE=$(SERVICE) \
		--build-arg BUILD_DIR=$(BUILD_DIR) \
		-t $(IMAGE_TAG) -f $(DOCKERFILE_PATH) $(BUILD_DIR)

# Clean up built images
.PHONY: clean
clean:
ifeq ($(SERVICE),)
	# If SERVICE is empty, loop through all services and remove images
	$(foreach service,$(SERVICES),docker rmi $(DOCKER_IMAGE_NAME)-$(service):$(VERSION) || true;)
else
	# Otherwise, remove the specified service image
	docker rmi $(IMAGE_TAG) || true
endif

# Push the built image(s) to a container registry
.PHONY: push
push:
ifeq ($(SERVICE),)
	# If SERVICE is empty, loop through all services and push
	$(foreach service,$(SERVICES),docker push $(DOCKER_IMAGE_NAME)-$(service):$(VERSION);)
else
	# Otherwise, push the specified service image
	docker push $(IMAGE_TAG)
endif

# Custom build with specific parameters
.PHONY: custom_build
custom_build:
	docker build --platform $(PLATFORM) \
		--build-arg PLATFORM=$(PLATFORM) \
		--build-arg HANDLER=$(SERVICE_HANDLER) \
		--build-arg HANDLER_FOLDER=$(SERVICE) \
		--build-arg SERVICE=$(SERVICE) \
		--build-arg BUILD_DIR=$(BUILD_DIR) \
		-t $(IMAGE_TAG) -f $(DOCKERFILE_PATH) $(BUILD_DIR)

# Run a specific Docker container (optional)
.PHONY: run
run:
	docker run --platform $(PLATFORM) --name $(DOCKER_IMAGE_NAME)-$(SERVICE) $(IMAGE_TAG)