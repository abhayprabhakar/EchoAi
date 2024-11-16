---

## **Building and Deploying EchoAi with Docker**

Follow these instructions to build and deploy the EchoAi application using Docker.

---

### **Prerequisites**
1. Ensure you have Docker installed on your system. You can download and install Docker from [here](https://www.docker.com/products/docker-desktop/).
2. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/abhayprabhakar/EchoAi.git
   cd EchoAi
   ```

---

### **API Endpoints**

EchoAi provides RESTful API endpoints for key functionalities:  
- `/llm`: Processes text input using the LLM API, with Retrieval-Augmented Generation (RAG) if documentation is available.  
- `/tts`: Converts a given text input into speech and returns the audio file.  
- `/stt`: Converts speech input into text.  

#### **Using the Endpoints**
- **LLM API** (`/llm`):  
  - Input: JSON containing user query text.  
  - Output: JSON with the processed response from the LLM.  

  Example:
  ```bash
  curl -X POST http://localhost:5000/llm -H "Content-Type: application/json" -d '{"query": "What is EchoAi?"}'
  ```

- **Text-to-Speech (TTS)** (`/tts`):  
  - Input: JSON containing the text to be converted.  
  - Output: Audio file.  

  Example:
  ```bash
  curl -X POST http://localhost:5000/tts -H "Content-Type: application/json" -d '{"text": "Hello, welcome to EchoAi!"}' --output output.mp3
  ```

- **Speech-to-Text (STT)** (`/stt`):  
  - Input: Audio file.  
  - Output: Transcribed text.  

  Example:
  ```bash
  curl -X POST http://localhost:5000/stt -H "Content-Type: multipart/form-data" -F "file=@audio_sample.wav"
  ```

---

### **Documentation for RAG**
EchoAi utilizes **Retrieval-Augmented Generation (RAG)** to provide accurate and context-aware responses. All **PDF** and **CSV** files placed in the `documentation` folder will be considered as the knowledge base for RAG.  

To include your own documentation:
1. Add your `.pdf` and `.csv` files to the `documentation` folder.
2. The application will automatically index these files and use them for generating responses.

---

### **Steps to Build and Run the Docker Container**

#### **1. Build the Docker Image**
Build the Docker image using the provided `Dockerfile`:
```bash
docker build -t echoai:latest .
```
- This command creates a Docker image named `echoai` with the `latest` tag.

#### **2. Run the Docker Container**
Run a container using the built image:
```bash
docker run -d -p 5000:5000 --name echoai-container echoai:latest
```
- `-d`: Runs the container in detached mode (in the background).
- `-p 5000:5000`: Maps port 5000 of the container to port 5000 on your host machine.
- `--name echoai-container`: Assigns a name to the container.

After this step, the EchoAi application will be accessible at `http://localhost:5000` in your web browser or via API endpoints.

#### **3. Environment Variables (Optional)**
If the application requires environment variables (e.g., API keys for LLM or STT), you can pass them during container creation using the `-e` flag:
```bash
docker run -d -p 5000:5000 --name echoai-container -e API_KEY=<your_api_key> echoai:latest
```

---

### **Using Custom Documentation**
To customize the RAG responses:
1. Place your `.pdf` and `.csv` files in the `documentation` folder.
2. Restart the container to re-index the documents:
   ```bash
   docker restart echoai-container
   ```

---

### **Stopping and Restarting the Container**

#### **Stop the Container**
To stop the running container:
```bash
docker stop echoai-container
```

#### **Start the Container Again**
To restart the container:
```bash
docker start echoai-container
```

#### **Remove the Container**
If you need to remove the container completely:
```bash
docker rm -f echoai-container
```

---

### **Updating the Application**
If you update the code, Dockerfile, or `documentation` folder, you’ll need to rebuild the Docker image:
1. Stop and remove the existing container:
   ```bash
   docker stop echoai-container
   docker rm echoai-container
   ```
2. Rebuild the image:
   ```bash
   docker build -t echoai:latest .
   ```
3. Run the container again:
   ```bash
   docker run -d -p 5000:5000 --name echoai-container echoai:latest
   ```

---

### **Logs and Debugging**
To view the logs of the running container:
```bash
docker logs echoai-container
```

For interactive debugging inside the container:
```bash
docker exec -it echoai-container /bin/bash
```

---

### **Deploying in Production**
For production deployment:
1. Use a reverse proxy like Nginx to handle HTTPS and routing.
2. Optionally, set up Docker Compose for easier multi-container orchestration.

---
