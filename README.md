# 🎯 AI-Powered PPT Generator

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> **Transform any content into professional presentations using cutting-edge AI and microservices architecture.**

A sophisticated full-stack application that automatically generates PowerPoint presentations from documents, YouTube videos, or text prompts using open-source AI models, built with a scalable microservices architecture and real-time processing capabilities.

![Demo GIF](./assets/demo.gif)

---

## 🌟 Key Features

### 🤖 **AI-Powered Content Generation**
- **Multi-Model Integration**: DeepSeek R1 for structured reasoning, Qwen2.5 for JSON outputs
- **Intelligent Slide Creation**: Context-aware content generation with logical flow
- **Dynamic Chart Generation**: AI-generated datasets and visualizations
- **Smart Image Integration**: Contextual image suggestions and placement

### 📄 **Multi-Format Input Support**
- **Document Processing**: PDF, DOCX, TXT with OCR capabilities
- **YouTube Integration**: Automatic transcript extraction and analysis
- **Direct Text Input**: Custom prompts and topic-based generation
- **Batch Processing**: Handle multiple inputs simultaneously

### 🏗️ **Enterprise-Grade Architecture**
- **Microservices Design**: Independent, scalable service components
- **Event-Driven Architecture**: Redis pub/sub for real-time communication
- **Multi-Level Caching**: Optimized performance with Redis and browser storage
- **Async Processing**: Background task handling with real-time status updates

### 🎨 **Interactive Frontend**
- **Real-Time Preview**: Live slide rendering during generation
- **Custom Slide Editor**: Drag-and-drop editing with instant preview
- **Responsive Design**: Mobile-first approach with touch navigation
- **Export Options**: PPTX, PDF, and web-shareable formats

---

## 🏛️ Architecture Overview

Gateway --> DocProcessor[Document Processor :8001]
Gateway --> AIGenerator[AI Generator :8002] 
Gateway --> Renderer[Presentation Renderer :8003]

DocProcessor --> Redis[(Redis)]
AIGenerator --> Redis
Renderer --> Redis

Gateway --> PostgreSQL[(PostgreSQL)]

Redis --> EventBus[Event Bus<br/>pub/sub]

AIGenerator --> DeepSeek[DeepSeek R1]
AIGenerator --> Qwen[Qwen2.5]

Renderer --> Charts[Chart.js/D3.js]
Renderer --> Export[python-pptx]


### 🔧 **Service Components**

| Service | Port | Responsibility | Tech Stack |
|---------|------|---------------|------------|
| **API Gateway** | 8000 | Request routing, authentication, rate limiting | FastAPI, Redis |
| **Document Processor** | 8001 | PDF/DOCX parsing, OCR, YouTube transcripts | python-docx, PyPDF2, pytesseract |
| **AI Generator** | 8002 | Content generation, slide structuring | DeepSeek R1, Qwen2.5, OpenAI |
| **Presentation Renderer** | 8003 | Slide assembly, chart generation, export | python-pptx, Chart.js |
| **Frontend** | 3000 | User interface, real-time updates | React, TypeScript, WebSocket |

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (v20.10+)
- **Node.js** (v18+) for local development
- **Python** (v3.11+) for local development
- **Git** for version control

### 🐳 One-Click Setup with Docker

Clone the repository
git clone https://github.com/yourusername/ppt-generator.git
cd ppt-generator

Start all services
docker-compose up -d

Verify services are running
docker-compose ps


### 🌐 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Main application interface |
| API Gateway | http://localhost:8000/docs | Interactive API documentation |
| Document Processor | http://localhost:8001/docs | Document processing endpoints |
| AI Generator | http://localhost:8002/docs | AI generation services |
| Presentation Renderer | http://localhost:8003/docs | Rendering and export APIs |

---

## 💻 Local Development

### Backend Services

Install Python dependencies for each service
cd services/gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd services/document-processor
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001


### Frontend Development

cd frontend
npm install
npm start


### Environment Variables

Create a `.env` file in the root directory:

AI Models
OPENAI_API_KEY=your_openai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

Database
POSTGRES_DB=ppt_generator
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_password

Redis
REDIS_URL=redis://localhost:6379

Security
JWT_SECRET_KEY=your_jwt_secret_here