---
title: Student Task Processor
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Student Task Processor

An AI-powered student task processing system that automatically generates web applications, deploys them to GitHub Pages, and handles evaluation workflows.

## Features

- 🤖 AI-powered code generation using AIPIPE/OpenAI
- 📚 GitHub repository creation and management
- 🌐 Automatic GitHub Pages deployment
- 🔄 Multi-round task processing (initial + revisions)
- 📝 Comprehensive logging and error handling
- 🐳 Docker-ready for cloud deployment

## Environment Variables

Set these in your Hugging Face Spaces settings:

- `AIPIPE_TOKEN`: Your AIPIPE API token (required)
- `github_token`: GitHub Personal Access Token with repo permissions (required)
- `secret`: Authentication secret for API access (required)
- `AIPIPE_URL`: AIPIPE service URL (optional, defaults to openrouter)

## API Endpoints

- `POST /process_task`: Process task requests and generate applications
- `GET /health`: Health check endpoint
- `GET /`: API information and documentation

## Usage

Send a POST request to `/process_task` with your task requirements and the system will:

1. Generate a complete web application using AI
2. Create a GitHub repository
3. Upload the generated files
4. Enable GitHub Pages
5. Return the repository and deployment URLs

Perfect for automated coding assignments and educational workflows!