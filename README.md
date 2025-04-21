# AI Portfolio Generator

A powerful AI-powered portfolio generator that transforms resume data into professional, customizable websites. Upload your resume, edit information, and generate a beautiful portfolio website with just a few clicks.

## Features

- **Resume Extraction**: Upload your resume (PDF) and automatically extract relevant information
- **AI-Powered Generation**: Uses Claude AI to create professional, customizable portfolio websites
- **Multiple Themes**: Choose from various themes including Professional Classic, Modern Minimalist, Netflix Style, Amazon Style, and more
- **Edit & Customize**: Edit extracted information and customize design elements before generating
- **Download Options**: Download as HTML file or ZIP package for easy deployment
- **Save & Manage**: Save your portfolios and access them anytime through your account
- **Easy Deployment**: Simple instructions for deploying to Netlify, Vercel, or GitHub Pages

## Technologies

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI**: Anthropic Claude (for resume parsing and portfolio generation)
- **Database**: PostgreSQL
- **PDF Processing**: PDFPlumber
- **HTML Generation**: AI-powered HTML, CSS, and JavaScript generation

## Getting Started

1. Visit the application at [AI Portfolio Generator](https://your-deploy-url.replit.app)
2. Upload your resume (PDF format)
3. Review and edit the extracted information
4. Select a theme and customize design options
5. Preview your portfolio
6. Generate and download your portfolio
7. Deploy it using the provided instructions

## How to Use

### 1. Upload Resume

- Go to the "Upload Resume" tab
- Upload your resume in PDF format
- Wait for the AI to extract your information

### 2. Customize Theme

- Go to the "Customize Theme" tab
- Edit any extracted information as needed
- Select a theme from the dropdown
- Choose accent colors and other customization options
- Click "Preview Theme" to see your portfolio

### 3. Generate & Download

- Go to the "Generate & Download" tab
- Review your final portfolio
- Enter your email to save your portfolio
- Download your portfolio as an HTML file or ZIP package
- Follow the deployment instructions to publish your portfolio online

### 4. My Portfolios

- Access your saved portfolios in the "My Portfolios" page
- View, edit, or delete your existing portfolios

## Deployment

This application consists of two components:
- A Streamlit frontend running on port 5000
- A FastAPI backend running on port 8000

Both services are required for the application to function properly.

## Privacy

- Your resume data is processed securely
- API keys are handled with proper security measures
- Save your portfolios to access them later