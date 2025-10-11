#!/bin/bash

# Deployment helper script for Hugging Face Spaces
echo "🚀 Preparing for Hugging Face Spaces deployment..."

# Check if required files exist
echo "📋 Checking required files..."
required_files=("Dockerfile" "requirements.txt" "main.py" ".env.example")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing!"
        exit 1
    fi
done

echo ""
echo "📝 Deployment checklist:"
echo "1. ✅ Create a new Hugging Face Space"
echo "2. ✅ Choose 'Docker' as the SDK"
echo "3. ✅ Connect your GitHub repository: https://github.com/23f1002487/tds-p1"
echo "4. ✅ Set the following environment variables in HF Spaces settings:"
echo "   - AIPIPE_TOKEN=your_aipipe_token"
echo "   - github_token=your_github_pat" 
echo "   - secret=your_secret_key"
echo "5. ✅ Optional: Set AIPIPE_URL if using custom endpoint"
echo ""
echo "🌐 Your app will be available at: https://your-username-your-space-name.hf.space"
echo "📚 API docs will be at: https://your-username-your-space-name.hf.space/docs"
echo ""
echo "🎉 Ready to deploy!"