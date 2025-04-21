from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_pdf(text_file, pdf_file):
    # Create a canvas
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter
    
    # Set font
    c.setFont("Helvetica", 12)
    
    # Get content from text file
    with open(text_file, 'r') as file:
        lines = file.readlines()
    
    # Start at the top of the page
    y = height - 50
    
    # Add lines of text
    for line in lines:
        if line.strip():  # Skip empty lines
            c.drawString(50, y, line.strip())
        y -= 15  # Move down for the next line
        
        # If we're near the bottom, start a new page
        if y < 50:
            c.showPage()
            y = height - 50
    
    # Save the PDF
    c.save()

# Create a sample PDF
create_pdf("sample_resume.txt", "sample_resume.pdf")
print("PDF created successfully!")