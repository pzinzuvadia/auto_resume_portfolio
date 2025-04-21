from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
import io
import os
from typing import Optional
import base64

from resume_processor import ResumeProcessor
from portfolio_generator import PortfolioGenerator

app = FastAPI(
    title="Portfolio Generator API",
    description="API for generating portfolio websites from resumes",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Portfolio Generator API is running"}

@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """
    Extract information from a resume.
    
    Args:
        file: Uploaded resume file.
        
    Returns:
        JSON with extracted resume information.
    """
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the resume
        result = ResumeProcessor.process_resume(io.BytesIO(file_content))
        
        return JSONResponse(
            content={"status": "success", "data": result},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.post("/generate-portfolio")
async def generate_portfolio(
    resume_data: str = Form(...),
    theme: str = Form(...),
    claude_api_key: str = Form(...)
):
    """
    Generate a portfolio website.
    
    Args:
        resume_data: JSON string containing resume information.
        theme: Selected theme for the portfolio.
        claude_api_key: API key for Anthropic's Claude.
        
    Returns:
        JSON with generated portfolio HTML.
    """
    try:
        # Parse resume data
        resume_info = eval(resume_data)
        
        # Initialize portfolio generator
        generator = PortfolioGenerator(claude_api_key)
        
        # Generate portfolio
        html_content = generator.generate_portfolio(resume_info, theme)
        
        # Create base64 data URI for preview
        data_uri = generator.encode_html_to_data_uri(html_content)
        
        # Create downloadable ZIP
        zip_content = generator.create_zip_file(html_content)
        zip_base64 = base64.b64encode(zip_content).decode('utf-8')
        
        return JSONResponse(
            content={
                "status": "success", 
                "html": html_content,
                "preview_uri": data_uri,
                "zip_base64": zip_base64
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/themes")
async def get_themes():
    """
    Get available theme options.
    
    Returns:
        JSON with theme options.
    """
    try:
        from theme_templates import ThemeTemplates
        themes = ThemeTemplates.get_theme_options()
        return JSONResponse(
            content={"status": "success", "themes": themes},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
