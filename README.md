---
title: TDS P1 Web App Generator
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# TDS P1 Web App Generator 🚀

**AI-powered web application generator that creates, deploys, and manages student coding projects automatically.**

## 🎯 What it does

This intelligent system receives task briefs and automatically:
- 🤖 **Generates** complete web applications (HTML/CSS/JS) using AI
- 📦 **Creates** GitHub repositories with proper structure
- 🌐 **Deploys** to GitHub Pages instantly
- 🔄 **Processes** feedback for iterative improvements

## 🔧 Key Features

- **AI-Powered**: Uses AIPIPE/OpenAI models for intelligent code generation
- **Automated Deployment**: One-click GitHub Pages deployment
- **Task Management**: Handles initial projects and revisions
- **RESTful API**: Clean endpoints for easy integration
- **Educational Focus**: Designed for academic assignments

## 🚀 API Endpoints

- **`POST /process_task`** - Submit a coding task and get a deployed web app
- **`GET /health`** - Check system status and configuration
- **`GET /docs`** - Interactive API documentation
- **`GET /`** - API information

## 📋 Required Environment Variables

Set these in your Hugging Face Spaces settings:

- **`OPENAI_API_KEY`** - Your AIPIPE token (use AIPIPE token here for compatibility) (required)
- **`OPENAI_BASE_URL`** - AIPIPE service URL: `https://aipipe.org/openrouter/v1` (required)
- **`github_token`** - GitHub Personal Access Token with repo permissions (required)
- **`secret`** - Authentication secret for API access (required)

## 🎓 Usage Example

```json
POST /process_task
{
  "email": "student@example.com",
  "secret": "your_secret_key",
  "task": "calculator-app",
  "round": 1,
  "nonce": "unique-id",
  "brief": "Create a calculator app with basic arithmetic operations",
  "checks": ["Has working buttons", "Performs calculations", "Responsive design"],
  "evaluation_url": "https://your-evaluation-endpoint.com"
}
```

**Response:**
```json
{
  "email": "student@example.com",
  "task": "calculator-app",
  "round": 1,
  "nonce": "unique-id",
  "repo_url": "https://github.com/username/calculator-app-unique-id",
  "commit_sha": "abc123...",
  "pages_url": "https://username.github.io/calculator-app-unique-id"
}
```

## 🏗️ Architecture

- **FastAPI** - Modern Python web framework
- **Pydantic AI** - Type-safe AI integration
- **GitHub API** - Repository and Pages management
- **Docker** - Containerized deployment
- **AIPIPE** - AI service integration

## 🎯 Built for Education

Perfect for instructors and students working on web development projects. Streamlines the entire workflow from assignment brief to deployed application.

---

*Powered by FastAPI, Pydantic AI, and GitHub API*# Health endpoint debug - Wed Oct 15 10:42:10 WAT 2025
