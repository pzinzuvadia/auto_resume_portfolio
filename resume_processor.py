import pdfplumber
import io
import re

class ResumeProcessor:
    """
    Processes and extracts structured information from resumes.
    """
    
    @staticmethod
    def extract_text_from_pdf(file):
        """
        Extract all text from a PDF file.
        
        Args:
            file: Uploaded PDF file.
            
        Returns:
            String containing all extracted text.
        """
        extracted_text = ""
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            return extracted_text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def extract_sections(text):
        """
        Extract sections from resume text.
        
        Args:
            text: String containing the resume text.
            
        Returns:
            Dictionary with section names as keys and content as values.
        """
        # Common section headers in resumes
        section_patterns = [
            r'(?i)(EDUCATION|ACADEMIC BACKGROUND)',
            r'(?i)(EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|PROFESSIONAL EXPERIENCE)',
            r'(?i)(SKILLS|TECHNICAL SKILLS|KEY SKILLS)',
            r'(?i)(PROJECTS|KEY PROJECTS)',
            r'(?i)(CERTIFICATIONS|CERTIFICATES)',
            r'(?i)(PUBLICATIONS|RESEARCH)',
            r'(?i)(AWARDS|HONORS|ACHIEVEMENTS)',
            r'(?i)(VOLUNTEER|COMMUNITY SERVICE)',
            r'(?i)(LANGUAGES|LANGUAGE PROFICIENCY)',
            r'(?i)(INTERESTS|HOBBIES)'
        ]
        
        # Combine patterns into a single regex
        combined_pattern = '|'.join(section_patterns)
        
        # Find all section headers
        matches = list(re.finditer(combined_pattern, text))
        
        sections = {}
        if not matches:
            # If no sections found, treat the entire text as one section
            sections["General Information"] = text
            return sections
        
        # Extract each section
        for i, match in enumerate(matches):
            section_name = match.group(0).strip()
            start_index = match.start()
            
            # Determine the end of the current section
            if i < len(matches) - 1:
                end_index = matches[i + 1].start()
            else:
                end_index = len(text)
            
            # Extract section content
            section_content = text[start_index:end_index].strip()
            sections[section_name] = section_content
        
        # Extract header information (assume it's before the first section)
        if matches and matches[0].start() > 0:
            header_text = text[:matches[0].start()].strip()
            sections["Personal Information"] = header_text
        
        return sections

    @staticmethod
    def extract_email(text):
        """Extract email address from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ""

    @staticmethod
    def extract_phone(text):
        """Extract phone number from text."""
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        matches = re.findall(phone_pattern, text)
        return matches[0] if matches else ""

    @staticmethod
    def extract_name(text, sections):
        """
        Attempt to extract name from the resume.
        Often the name is the first line of the resume or in the Personal Information section.
        """
        if "Personal Information" in sections:
            lines = sections["Personal Information"].split('\n')
            if lines:
                # Typically, the name is the first line in the personal information section
                return lines[0].strip()
        
        # If not found in Personal Information, try the first line of the resume
        lines = text.split('\n')
        if lines:
            return lines[0].strip()
        
        return ""

    @staticmethod
    def process_resume(file):
        """
        Process resume file and extract structured information.
        
        Args:
            file: Uploaded resume file (PDF).
            
        Returns:
            Dictionary containing structured resume information.
        """
        if file is None:
            raise ValueError("No file provided")
            
        try:
            file_content = file.read()
            file.seek(0)
            
            # Extract text from the resume
            full_text = ResumeProcessor.extract_text_from_pdf(io.BytesIO(file_content))
            
            # Extract sections
            sections = ResumeProcessor.extract_sections(full_text)
            
            # Extract key information
            email = ResumeProcessor.extract_email(full_text)
            phone = ResumeProcessor.extract_phone(full_text)
            name = ResumeProcessor.extract_name(full_text, sections)
            
            return {
                "full_text": full_text,
                "sections": sections,
                "email": email,
                "phone": phone,
                "name": name
            }
            
        except Exception as e:
            raise Exception(f"Error processing resume: {str(e)}")
