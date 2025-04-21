class ThemeTemplates:
    """
    Provides portfolio website templates with different themes.
    """
    
    @staticmethod
    def get_theme_options():
        """
        Returns a list of available theme options.
        
        Returns:
            List of theme names.
        """
        return [
            "Professional Classic",
            "Modern Minimalist",
            "Netflix Style",
            "Amazon Style",
            "Creative Portfolio",
            "Tech Professional"
        ]
    
    @staticmethod
    def get_system_prompt(theme):
        """
        Returns the system prompt for Claude API based on the selected theme.
        
        Args:
            theme: Selected theme name.
            
        Returns:
            System prompt for Claude API.
        """
        base_prompt = (
            "You are an expert web developer specializing in creating professional portfolio websites. "
            "Generate complete, responsive HTML and CSS for a portfolio website that showcases a person's "
            "professional experience, skills, education, and projects. Your code must be modern, visually "
            "appealing, and follow best practices. Include all HTML, CSS, and JavaScript in a single file."
        )
        
        theme_specific_instructions = {
            "Professional Classic": (
                "Create a classic, professional portfolio with a clean, corporate aesthetic. Use navy blue, "
                "white, and gray as the primary colors. The layout should be straightforward with clear sections "
                "and conservative styling suitable for traditional industries like finance, law, or consulting."
            ),
            "Modern Minimalist": (
                "Design a minimalist portfolio with ample white space, subtle animations, and a focus on "
                "typography. Use a monochromatic color scheme with one accent color. The layout should be "
                "grid-based with asymmetrical elements for visual interest."
            ),
            "Netflix Style": (
                "Create a Netflix-inspired dark theme with a black background, red accents (Netflix red), and "
                "card-based content layout. Use a horizontal scrolling mechanism for project showcases. "
                "Include subtle hover effects and transitions similar to the Netflix UI."
            ),
            "Amazon Style": (
                "Design an Amazon-inspired layout with a light background, Amazon blue accents, and a "
                "user-friendly, information-rich design. Include clearly defined sections with card-based "
                "elements, rating-style skill indicators, and a navigation bar similar to Amazon's interface."
            ),
            "Creative Portfolio": (
                "Create an artistic portfolio with bold colors, unusual layouts, and creative elements. "
                "Use animations, gradients, and artistic typography. The design should be unconventional "
                "yet functional, suitable for creative professionals."
            ),
            "Tech Professional": (
                "Design a tech-focused portfolio with a dark mode aesthetic, code-like elements, and tech-inspired "
                "visuals. Use a terminal/code editor inspired color scheme (dark background with bright syntax "
                "highlighting colors). Include coding-inspired animations and tech iconography."
            )
        }
        
        accessibility_requirements = (
            "Ensure the website is accessible following WCAG guidelines. Use semantic HTML, "
            "provide alt text for images, ensure sufficient color contrast, and make sure the site "
            "is keyboard navigable. The website must be fully responsive and work well on mobile devices."
        )
        
        output_requirements = (
            "Your output must be a complete, ready-to-use HTML file that includes all CSS and JavaScript. "
            "Design the portfolio for a standard web developer, incorporating the person's information "
            "from their resume in a sensible way. Create a professional, aesthetically pleasing result "
            "that highlights their skills and experience."
        )
        
        specific_instructions = theme_specific_instructions.get(theme, theme_specific_instructions["Professional Classic"])
        
        return f"{base_prompt} {specific_instructions} {accessibility_requirements} {output_requirements}"
