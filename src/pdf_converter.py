"""
PDF conversion utilities for the email app.
"""
from pathlib import Path
from typing import List, Tuple
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
import streamlit as st
import tempfile
import os

from config import APP_CONFIG


class PDFConverter:
    """Handles PDF to image conversion."""
    
    def __init__(self, quality: int = 85, max_size: Tuple[int, int] = (800, 800)):
        self.supported_types = APP_CONFIG["supported_file_types"]
        self.max_size = max_size
        self.quality = quality
        self.format = APP_CONFIG["image_format"]
    
    def validate_file(self, uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file type and size."""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension not in self.supported_types:
            return False, f"Unsupported file type: {file_extension}"
        
        # Check file size (limit to 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            return False, "File size too large (max 50MB)"
        
        return True, ""
    
    def convert_pdf_to_images(self, uploaded_file) -> List[BytesIO]:
        """
        Convert PDF file to list of image buffers.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            List of BytesIO buffers containing converted images
        """
        # Create a temporary file with proper cleanup
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Write uploaded file content to temporary file
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        
        try:
            # Convert PDF to images
            images = convert_from_path(temp_file_path)
            
            # Process images
            image_buffers = []
            for i, img in enumerate(images):
                buffer = BytesIO()
                
                # Resize image
                img.thumbnail(self.max_size)
                
                # Save to buffer
                img.save(buffer, format=self.format, quality=self.quality)
                buffer.seek(0)
                image_buffers.append(buffer)
            
            return image_buffers
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                # File might already be deleted or not accessible
                pass
    
    def display_images(self, image_buffers: List[BytesIO]) -> None:
        """Display converted images in Streamlit."""
        st.write("Converted Images:")
        
        with st.expander("Click to view converted images"):
            for i, buffer in enumerate(image_buffers):
                buffer.seek(0)
                img = Image.open(buffer)
                st.image(img, caption=f"Page {i+1}", use_column_width=True) 