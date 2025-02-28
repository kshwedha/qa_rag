OLLAMA_IMAGE = ollama/ollama
MODEL_NAME = llama3
DOCKERFILE_PATH = Dockerfile
IMAGE_NAME = qa_rag
TAG = 0.1

# Pull the Ollama Docker image
pull-ollama:
	docker pull $(OLLAMA_IMAGE)

# Run Ollama in a container
run-ollama:
	docker run -d --name ollama -p 11434:11434 --gpus all --restart always $(OLLAMA_IMAGE)

# Pull Llama3 model inside the running Ollama container
pull-model:
	docker exec ollama ollama pull $(MODEL_NAME)

# Check if Ollama is running
check-status:
	curl http://localhost:11434/api/tags || echo "Ollama is not running"

# Stop and remove the Ollama container
clean:
	docker stop ollama && docker rm ollama

docker-build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH)