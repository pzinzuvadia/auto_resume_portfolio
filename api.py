from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
import io
import os
import json
from typing import Optional, List
import base64
from sqlalchemy.orm import Session

from resume_processor import ResumeProcessor
from portfolio_generator import PortfolioGenerator
from database import get_db, User, Portfolio, Resume

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

@app.post("/save-portfolio")
async def save_portfolio(
    email: str = Form(...),
    resume_data: str = Form(...),
    theme: str = Form(...),
    html_content: str = Form(...),
    portfolio_name: str = Form("My Portfolio"),
    db: Session = Depends(get_db)
):
    """
    Save a generated portfolio to the database.
    
    Args:
        email: User's email.
        resume_data: JSON string containing resume information.
        theme: Selected theme for the portfolio.
        html_content: HTML content of the portfolio.
        portfolio_name: Name for the portfolio.
        
    Returns:
        JSON with saved portfolio ID.
    """
    # Implement retry logic for database operations
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Parse resume data
            resume_info = json.loads(resume_data)
            
            # Check if user exists, create if not
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(email=email)
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create new portfolio
            portfolio = Portfolio(
                user_id=user.id,
                name=portfolio_name,
                theme=theme,
                html_content=html_content
            )
            db.add(portfolio)
            db.commit()
            db.refresh(portfolio)
            
            # Create resume record
            resume = Resume(
                portfolio_id=portfolio.id,
                filename=resume_info.get("filename", "uploaded_resume.pdf"),
                content_text=resume_info.get("full_text", ""),
                extracted_name=resume_info.get("name", ""),
                extracted_email=resume_info.get("email", ""),
                extracted_phone=resume_info.get("phone", ""),
                sections_json=json.dumps(resume_info.get("sections", {}))
            )
            db.add(resume)
            db.commit()
            
            return JSONResponse(
                content={"status": "success", "portfolio_id": portfolio.id},
                status_code=200
            )
            
        except Exception as db_error:
            db.rollback()
            retry_count += 1
            
            # Log details about the error
            print(f"Database error on attempt {retry_count}/{max_retries}: {str(db_error)}")
            
            if "SSL connection has been closed unexpectedly" in str(db_error) or "connection already closed" in str(db_error):
                # These are connection issues that might be resolved with a retry
                print("Detected SSL/connection issue, will retry with a new session")
                
                # Wait before retrying
                import time
                time.sleep(1 * retry_count)  # Progressive backoff
                
                # Get a fresh DB session
                db.close()
                db = next(get_db())
            elif retry_count >= max_retries:
                # We've exhausted retries, return error to client
                return JSONResponse(
                    content={"status": "error", "message": f"Failed to save portfolio after {max_retries} attempts: {str(db_error)}"},
                    status_code=500
                )
            else:
                # For other errors, also retry but log differently
                print(f"Unexpected database error, retrying: {str(db_error)}")
                
                # Wait before retrying
                import time
                time.sleep(1 * retry_count)
                
                # Get a fresh DB session
                db.close()
                db = next(get_db())
    
    # This should not be reached but just in case
    return JSONResponse(
        content={"status": "error", "message": "Failed to save portfolio after multiple attempts, please try again later"},
        status_code=500
    )

@app.get("/user-portfolios/{email}")
async def get_user_portfolios(email: str, db: Session = Depends(get_db)):
    """
    Get all portfolios for a user.
    
    Args:
        email: User's email.
        
    Returns:
        JSON with list of portfolios.
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return JSONResponse(
                content={"status": "error", "message": "User not found"},
                status_code=404
            )
        
        # Get portfolios
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        
        # Format response
        portfolio_list = [
            {
                "id": p.id,
                "name": p.name,
                "theme": p.theme,
                "created_at": p.created_at.isoformat(),
                "is_favorite": p.is_favorite
            } for p in portfolios
        ]
        
        return JSONResponse(
            content={"status": "success", "portfolios": portfolio_list},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.get("/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Get a specific portfolio by ID.
    
    Args:
        portfolio_id: Portfolio ID.
        
    Returns:
        JSON with portfolio details.
    """
    try:
        # Get portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return JSONResponse(
                content={"status": "error", "message": "Portfolio not found"},
                status_code=404
            )
        
        # Get resume info
        resume = db.query(Resume).filter(Resume.portfolio_id == portfolio.id).first()
        
        # Format response
        portfolio_data = {
            "id": portfolio.id,
            "name": portfolio.name,
            "theme": portfolio.theme,
            "html_content": portfolio.html_content,
            "created_at": portfolio.created_at.isoformat(),
            "is_favorite": portfolio.is_favorite,
            "resume": {
                "name": resume.extracted_name if resume else "",
                "email": resume.extracted_email if resume else "",
                "phone": resume.extracted_phone if resume else "",
                "sections": json.loads(resume.sections_json) if resume and resume.sections_json else {}
            }
        }
        
        return JSONResponse(
            content={"status": "success", "portfolio": portfolio_data},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

@app.delete("/portfolio/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """
    Delete a portfolio.
    
    Args:
        portfolio_id: Portfolio ID.
        
    Returns:
        JSON with success message.
    """
    try:
        # Get portfolio
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if not portfolio:
            return JSONResponse(
                content={"status": "error", "message": "Portfolio not found"},
                status_code=404
            )
        
        # Delete associated resume
        db.query(Resume).filter(Resume.portfolio_id == portfolio.id).delete()
        
        # Delete portfolio
        db.delete(portfolio)
        db.commit()
        
        return JSONResponse(
            content={"status": "success", "message": "Portfolio deleted successfully"},
            status_code=200
        )
    except Exception as e:
        db.rollback()
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
