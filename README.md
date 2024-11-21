# EchoAi

**EchoAi** is an innovative tool designed to revolutionize customer support by enabling seamless, real-time voice interactions. It utilizes cutting-edge technologies to provide a smooth and efficient way for users to interact with automated support systems through natural conversation.
Here’s an example of a **Table of Contents** for your EchoAI README file. You can adjust it based on the sections of your project documentation:

---
## Table of Contents
1. [Key Features](#key-features)
2. [How It Works](#how-it-works)
3. [Use Cases](#use-cases)
4. [Technologies Used](#technologies-used)
5. [Vision](#vision)
6. [API Endpoints](#api-endpoints)
7. [Documentation for RAG](#documentation-for-rag)
8. [Building and Deploying EchoAi with Docker](#building-and-deploying-echoai-with-docker)
   - [Prerequisites](#prerequisites)
   - [Steps to Build and Run the Docker Container](#steps-to-build-and-run-the-docker-container)
   - [Using Custom Documentation](#using-custom-documentation)
   - [Stopping and Restarting the Container](#stopping-and-restarting-the-container)
   - [Updating the Application](#updating-the-application)
9. [Logs and Debugging](#logs-and-debugging)
10. [Deploying in Production](#deploying-in-production)
11. [Our Team✨](#our-team✨)

---
### **Key Features**
- **Speech-to-Text Conversion**: EchoAi accurately transcribes user voice input into text using advanced speech recognition algorithms.
- **Natural Language Processing**: The transcribed text is processed by a **Large Language Model (LLM)** with **Retrieval-Augmented Generation (RAG)**, allowing for intelligent and context-aware responses based on your specific product documentation or knowledge base.
- **Text-to-Speech Response**: The system converts the generated response back into a natural, human-like voice, enabling a fully conversational experience.
- **Custom Knowledge Integration**: Users can input custom documents, FAQs, or datasets, allowing EchoAi to deliver precise and tailored support responses.
- **Scalable and Modular Design**: Built with scalability in mind, EchoAi can easily adapt to various use cases, from small businesses to enterprise-level customer support.
- **Dockerized for Ease of Deployment**: The entire application is containerized using Docker, ensuring a simple, portable, and reproducible deployment process.

### **How It Works**
1. **User Interaction**: The user speaks into the system, initiating the support interaction.
2. **Voice-to-Text Conversion**: The spoken input is converted into text using Speech-to-Text (STT) technology.
3. **LLM with RAG**: The transcribed text is processed by an LLM that uses Retrieval-Augmented Generation to fetch relevant information from the provided knowledge base.
4. **Text-to-Voice Conversion**: The system converts the LLM's response into spoken output using Text-to-Speech (TTS) technology, completing the interaction loop.

### **Use Cases**
- Customer service helplines
- Product inquiry systems
- Automated support for FAQs
- Voice-enabled chatbots
- AI-powered IVR (Interactive Voice Response) systems

### **Technologies Used**
- **Speech-to-Text (STT)**: Converts user speech to text.
- **Large Language Model (LLM)**: Processes user queries intelligently.
- **Retrieval-Augmented Generation (RAG)**: Enhances response quality by integrating relevant external knowledge.
- **Text-to-Speech (TTS)**: Delivers responses in a natural voice.
- **Docker**: Ensures a seamless and portable deployment process.

### **Vision**
EchoAi aims to redefine customer support by providing a natural, efficient, and scalable solution that reduces the workload on human support teams while improving customer satisfaction.

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
docker run -d -p 5000:5000 --name echoai-container -e GROQ_API_KEY=<your_api_key> -e AZURE_API_KEY=<your_api_key> -e AZURE_REGION=<azure_region> echoai:latest
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
# Our Team✨
<a href="https://github.com/abhayprabhakar" style="text-decoration: none"><img src="https://contrib.rocks/image?repo=abhayprabhakar/abhayprabhakar"/></a>
<a href="https://github.com/devady" style="text-decoration: none"><img src="https://contrib.rocks/image?repo=devady/devady"/></a>
<a href="https://github.com/toxicskulll" style="text-decoration: none"><img src="https://contrib.rocks/image?repo=toxicskulll/pmgdemo"/></a>
<a href="https://github.com/knighthyper" style="text-decoration: none"><img src="https://contrib.rocks/image?repo=knighthyper/clone"/></a>

Made with [contrib.rocks](https://contrib.rocks).
