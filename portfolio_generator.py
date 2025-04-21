import anthropic
import zipfile
import os
import io
import base64
import httpx
import json

class PortfolioGenerator:
    """
    Generates portfolio websites using Claude API.
    """
    
    def __init__(self, claude_api_key):
        """
        Initialize the portfolio generator with Claude API key.
        
        Args:
            claude_api_key: API key for Anthropic's Claude.
        """
        self.client = anthropic.Anthropic(api_key=claude_api_key)
        # the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        self.model = "claude-3-5-sonnet-20241022"
    
    def create_prompt(self, resume_data, theme_preferences):
        """
        Create a prompt for Claude API to generate a portfolio website.
        
        Args:
            resume_data: Dictionary containing extracted resume information.
            theme_preferences: User-defined theme preferences.
            
        Returns:
            String containing the prompt for Claude API.
        """
        full_name = resume_data.get("name", "")
        email = resume_data.get("email", "")
        phone = resume_data.get("phone", "")
        
        # Special parsing for each section type
        sections_text = ""
        for section_name, section_content in resume_data.get("sections", {}).items():
            if section_name.upper() == "EXPERIENCE":
                sections_text += f"## EXPERIENCE\n"
                # Process the experience section to clearly separate multiple experiences
                experiences = self._parse_experiences(section_content)
                for i, exp in enumerate(experiences):
                    sections_text += f"### Experience {i+1}\n{exp}\n\n"
            else:
                sections_text += f"## {section_name}\n{section_content}\n\n"
        
        prompt = (
            f"Create a professional portfolio website for {full_name}.\n\n"
            f"Contact information:\n"
            f"- Email: {email}\n"
            f"- Phone: {phone} (IMPORTANT: Make sure to display this exact phone number in the portfolio)\n\n"
            f"Resume content:\n{sections_text}\n"
            f"Design preferences: {theme_preferences}\n\n"
            "Generate a complete HTML file that includes all CSS and JavaScript needed for "
            "a responsive, modern portfolio website. The website should be a single HTML file "
            "that looks professional and showcases the person's skills and experience effectively.\n\n"
            "IMPORTANT GUIDELINES:\n"
            "1. Make sure to include ALL experiences listed in the resume, not just the most recent one.\n"
            "2. Display the exact phone number provided above - this is critical.\n"
            "3. Create separate sections or cards for each work experience.\n"
            "4. List each experience with its job title, company, dates, and bullet points.\n"
            "5. Make sure the contact information is prominently displayed and accurate.\n"
        )
        
        return prompt
        
    def _parse_experiences(self, experience_text):
        """
        Parse the experience section to identify individual experiences.
        
        Args:
            experience_text: Text content of the experience section.
            
        Returns:
            List of separate experience entries.
        """
        import re
        
        # First, try to split by company or job titles
        # Common patterns like "Software Developer, Company" or "Company - Position"
        experiences = []
        
        # Try to split by date ranges as they typically separate different jobs
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\s,]+\d{4}\s*[-–—]\s*(?:Present|Current|January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:[\s,]+\d{4})?'
        
        # Split the experience text by date pattern
        date_matches = list(re.finditer(date_pattern, experience_text, re.IGNORECASE))
        
        if date_matches:
            # If we found date patterns, use them to split the text
            last_end = 0
            for i, match in enumerate(date_matches):
                start = match.start()
                
                # Skip if this is part of a previous experience
                if start < last_end:
                    continue
                
                # Find the beginning of this experience (typically a job title or company name)
                # Look for the previous line break before the date
                prev_break = experience_text.rfind('\n', 0, start)
                if prev_break == -1:
                    prev_break = 0
                
                # Extract the experience, going back to include the job title
                if i < len(date_matches) - 1:
                    # For all but the last experience, go to the next date match
                    next_match = date_matches[i + 1]
                    end = next_match.start()
                    
                    # But find the line break before to get a clean break
                    prev_break_next = experience_text.rfind('\n', 0, end)
                    if prev_break_next > start:  # Make sure we're not going backwards
                        end = prev_break_next
                    
                    experiences.append(experience_text[prev_break:end].strip())
                    last_end = end
                else:
                    # For the last experience, go to the end
                    experiences.append(experience_text[prev_break:].strip())
                    
            # If we didn't parse any experiences, fall back to the full text
            if not experiences:
                experiences = [experience_text]
        else:
            # If we can't find date patterns, try splitting by job titles
            job_pattern = r'\n[A-Z][a-zA-Z\s,]+(Developer|Engineer|Designer|Manager|Director|Analyst|Consultant|Specialist|Coordinator|Assistant|Lead|Head|Chief|Officer|Administrator|Supervisor)'
            job_matches = list(re.finditer(job_pattern, '\n' + experience_text, re.IGNORECASE))
            
            if job_matches:
                # If we found job title patterns, use them to split the text
                for i, match in enumerate(job_matches):
                    start = match.start()
                    
                    # Skip the leading newline
                    if start == 0:
                        start = 1
                    
                    if i < len(job_matches) - 1:
                        end = job_matches[i + 1].start()
                        experiences.append(experience_text[start:end].strip())
                    else:
                        experiences.append(experience_text[start:].strip())
                        
                # If we didn't parse any experiences, fall back to the full text
                if not experiences:
                    experiences = [experience_text]
            else:
                # If we can't find any patterns, just use the whole text as one experience
                experiences = [experience_text]
        
        return experiences
    
    def generate_portfolio(self, resume_data, theme):
        """
        Generate a portfolio website using Claude API.
        
        Args:
            resume_data: Dictionary containing extracted resume information.
            theme: Selected theme for the portfolio.
            
        Returns:
            Generated HTML code for the portfolio website.
        """
        try:
            from theme_templates import ThemeTemplates
            system_prompt = ThemeTemplates.get_system_prompt(theme)
            user_prompt = self.create_prompt(resume_data, theme)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            html_content = response.content[0].text
            
            # Extract HTML code between ```html and ```
            html_pattern = r"```html\s*([\s\S]*?)\s*```"
            import re
            html_match = re.search(html_pattern, html_content)
            
            if html_match:
                return html_match.group(1)
            else:
                return html_content  # Return full response if no HTML code block found
        
        except Exception as e:
            raise Exception(f"Error generating portfolio: {str(e)}")
    
    def create_zip_file(self, html_content, filename="portfolio"):
        """
        Create a ZIP file containing the portfolio website.
        
        Args:
            html_content: HTML code for the portfolio website.
            filename: Base name for the files.
            
        Returns:
            ZIP file as bytes.
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename}.html", html_content)
            zip_file.writestr("README.txt", (
                "Portfolio Website\n"
                "=================\n\n"
                "This portfolio website was generated by AI Portfolio Generator.\n\n"
                "To view the website, simply open the HTML file in any web browser.\n"
                "The website is self-contained and does not require any external files or internet connection.\n\n"
                "For deployment to services like Netlify or Vercel:\n"
                "1. Upload the HTML file to your GitHub repository\n"
                "2. Connect your repository to Netlify/Vercel\n"
                "3. Follow their deployment instructions\n\n"
                "Enjoy your new portfolio website!"
            ))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def encode_html_to_data_uri(self, html_content):
        """
        Encode HTML content as a data URI for preview.
        
        Args:
            html_content: HTML code for the portfolio website.
            
        Returns:
            Data URI for the HTML content.
        """
        encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        return f"data:text/html;base64,{encoded_html}"
