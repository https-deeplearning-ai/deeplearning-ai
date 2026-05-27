"""
Visual Grounding Helper Functions
Utilities for creating annotated images with bounding boxes from document chunks
"""

import json
import boto3
from typing import Dict, List, Optional, Tuple
import io
from pathlib import Path

# Check if dynamic cropping dependencies are available
try:
    import fitz  # PyMuPDF for PDF rendering
    from PIL import Image, ImageDraw, ImageFont
    DYNAMIC_CROPPING_ENABLED = True
except ImportError:
    DYNAMIC_CROPPING_ENABLED = False

# Constants
CHUNK_IMAGES_PATH = "chunk_images"
DEFAULT_DPI = 150
DEFAULT_PADDING = 20
BOX_COLOR = "red"
BOX_WIDTH = 3


def render_pdf_page(pdf_bytes: bytes, page_num: int, dpi: int = 150):
    """
    Render a PDF page to PIL image.
    
    Args:
        pdf_bytes: PDF file content as bytes
        page_num: Page number (0-indexed)
        dpi: Resolution for PDF rendering (default 150)
    
    Returns:
        Tuple of (PIL Image, page_width, page_height) or (None, None, None) if disabled
    """
    if not DYNAMIC_CROPPING_ENABLED:
        return None, None, None
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[page_num]
        mat = fitz.Matrix(dpi/72.0, dpi/72.0)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_width, page_height = page.rect.width, page.rect.height
        doc.close()
        return img, page_width, page_height
    except Exception as e:
        print(f"Error rendering PDF page: {e}")
        return None, None, None


def extract_chunk_image(
    s3_client,
    bucket: str,
    source_pdf_key: str,
    bbox: List[float],
    page_num: int,
    chunk_id: str,
    source_document: str,
    highlight: bool = True,
    padding: int = 10
) -> Optional[str]:
    """
    Dynamically extract and crop a specific chunk from PDF stored in S3.
    
    Args:
        s3_client: Boto3 S3 client
        bucket: S3 bucket name
        source_pdf_key: S3 key of the source PDF
        bbox: [x0, y0, x1, y1] in NORMALIZED coordinates (0-1 range)
        page_num: Page number (0-indexed)
        chunk_id: Unique chunk identifier
        source_document: Document name without extension
        highlight: Add red border around chunk (default True)
        padding: Extra pixels around bbox (default 10)
    
    Returns:
        S3 presigned URL of the cropped chunk image or None
    """
    if not DYNAMIC_CROPPING_ENABLED:
        print("⚠️ Dynamic cropping disabled. Install PyMuPDF and Pillow.")
        return None
    
    try:
        # Check if chunk image already exists
        image_key = f"output/medical_chunk_images/{source_document}_{chunk_id}.png"
        try:
            s3_client.head_object(Bucket=bucket, Key=image_key)
            # Image exists, return presigned URL
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': image_key},
                ExpiresIn=3600
            )
            return presigned_url
        except:
            pass  # Image doesn't exist, create it
        
        # Download PDF from S3
        response = s3_client.get_object(Bucket=bucket, Key=source_pdf_key)
        pdf_bytes = response['Body'].read()
        
        # Render the PDF page
        img, page_width, page_height = render_pdf_page(pdf_bytes, page_num)
        
        if img is None:
            return None
        
        # If no bbox or invalid bbox, return full page
        if not bbox or len(bbox) != 4:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            image_data = img_bytes.getvalue()
        else:
            # Extract normalized bbox coordinates (0-1 range)
            norm_x0, norm_y0, norm_x1, norm_y1 = bbox
            
            # Convert normalized coordinates to PDF points
            pdf_x0 = norm_x0 * page_width
            pdf_y0 = norm_y0 * page_height
            pdf_x1 = norm_x1 * page_width
            pdf_y1 = norm_y1 * page_height
            
            # Scale PDF points to image pixels
            scale_x = img.width / page_width
            scale_y = img.height / page_height
            
            # Apply scaling and padding
            crop_x0 = max(0, int(pdf_x0 * scale_x) - padding)
            crop_y0 = max(0, int(pdf_y0 * scale_y) - padding)
            crop_x1 = min(img.width, int(pdf_x1 * scale_x) + padding)
            crop_y1 = min(img.height, int(pdf_y1 * scale_y) + padding)
            
            # Crop to chunk region
            chunk_img = img.crop((crop_x0, crop_y0, crop_x1, crop_y1))
            
            # Add red border highlight
            if highlight:
                draw = ImageDraw.Draw(chunk_img)
                draw.rectangle(
                    [padding, padding, chunk_img.width - padding - 1, chunk_img.height - padding - 1],
                    outline="red",
                    width=3
                )
            
            # Convert to PNG bytes
            img_bytes = io.BytesIO()
            chunk_img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            image_data = img_bytes.getvalue()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=image_key,
            Body=image_data,
            ContentType='image/png'
        )
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': image_key},
            ExpiresIn=3600
        )
        
        return presigned_url
        
    except Exception as e:
        print(f"Error extracting chunk image: {e}")
        return None


def create_annotated_image_from_pdf(
    pdf_bytes: bytes,
    page_num: int,
    bounding_boxes: List[Dict],
    output_s3_key: str,
    s3_client,
    bucket: str,
    dpi: int = 150,
    chunk_type: str = "text"
) -> str:
    """
    Create an annotated image from a PDF page with bounding boxes
    
    Args:
        pdf_bytes: PDF file content as bytes
        page_num: Page number (1-indexed)
        bounding_boxes: List of bounding box dictionaries with 'left', 'top', 'right', 'bottom'
        output_s3_key: S3 key for the output annotated image
        s3_client: Boto3 S3 client
        bucket: S3 bucket name
        dpi: Resolution for PDF rendering
        chunk_type: Type of chunk for color coding
    
    Returns:
        S3 URL of the uploaded annotated image
    """
    try:
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Get the specific page (0-indexed in PyMuPDF)
        page = pdf_document[page_num - 1] if page_num > 0 else pdf_document[page_num]
        
        # Render page to image at specified DPI
        mat = fitz.Matrix(dpi/72.0, dpi/72.0)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        
        # Open image with PIL
        img = Image.open(io.BytesIO(img_data))
        draw = ImageDraw.Draw(img)
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Define colors based on chunk type (matching ADE chunk types)
        CHUNK_TYPE_COLORS = {
            "text": (40, 167, 69),           # Green
            "table": (0, 123, 255),          # Blue  
            "marginalia": (111, 66, 193),    # Purple
            "figure": (255, 0, 255),         # Magenta
            "logo": (144, 238, 144),         # Light green
            "card": (255, 165, 0),           # Orange
            "attestation": (0, 255, 255),    # Cyan
            "scancode": (255, 193, 7),       # Yellow
            "form": (220, 20, 60),           # Red
            "tablecell": (173, 216, 230),    # Light blue
            "default": (128, 128, 128)       # Gray for unknown types
        }
        # Get RGB color based on chunk type
        rgb_color = CHUNK_TYPE_COLORS.get(chunk_type.lower(), CHUNK_TYPE_COLORS["default"])
        
        # Draw bounding boxes
        for bbox in bounding_boxes:
            if bbox and 'left' in bbox:
                # The coordinates from ADE are normalized (0-1) relative to the PDF page
                # Convert to pixel coordinates for the rendered image
                left = float(bbox.get('left', 0))
                top = float(bbox.get('top', 0))
                right = float(bbox.get('right', 1))
                bottom = float(bbox.get('bottom', 1))
                
                # Ensure coordinates are in 0-1 range
                left = max(0, min(1, left))
                top = max(0, min(1, top))
                right = max(0, min(1, right))
                bottom = max(0, min(1, bottom))
                
                # Convert to pixel coordinates
                x1 = int(left * img_width)
                y1 = int(top * img_height)
                x2 = int(right * img_width)
                y2 = int(bottom * img_height)
                
                # Draw rectangle with thick outline for visibility
                draw.rectangle(
                    [x1, y1, x2, y2],
                    outline=rgb_color,
                    width=3
                )
                
                # Add semi-transparent overlay for better visibility
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Create semi-transparent version of the RGB color
                fill_color = rgb_color + (30,)  # Add alpha channel for transparency
                
                overlay_draw.rectangle(
                    [x1, y1, x2, y2],
                    fill=fill_color
                )
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=output_s3_key,
            Body=img_bytes.getvalue(),
            ContentType='image/png'
        )
        
        pdf_document.close()
        
        # Generate presigned URL for the image
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': output_s3_key},
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        return presigned_url
        
    except Exception as e:
        print(f"Error creating annotated image: {e}")
        return None


def get_or_create_annotated_image(
    s3_client,
    bucket: str,
    source_pdf_key: str,
    chunk_id: str,
    grounding_info: Dict,
    chunk_type: str = "text",
    force_recreate: bool = False
) -> Optional[str]:
    """
    Get existing annotated image or create a new one
    
    Args:
        s3_client: Boto3 S3 client
        bucket: S3 bucket name
        source_pdf_key: S3 key of the source PDF
        chunk_id: Unique chunk identifier
        grounding_info: Dictionary with 'page' and 'box' information
        force_recreate: Force recreation even if image exists
    
    Returns:
        URL of the annotated image or None if failed
    """
    # Generate annotation key
    page_num = grounding_info.get('page', 1)
    clean_chunk_id = chunk_id.replace('<a id=', '').replace('></a>', '').strip('"')
    annotation_key = f"annotations/{Path(source_pdf_key).stem}_p{page_num}_{clean_chunk_id}.png"
    
    # Check if annotation already exists
    if not force_recreate:
        try:
            s3_client.head_object(Bucket=bucket, Key=annotation_key)
            # Generate presigned URL for existing annotation
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': annotation_key},
                ExpiresIn=3600  # URL valid for 1 hour
            )
            return presigned_url
        except:
            pass  # File doesn't exist, create it
    
    # Download source PDF
    try:
        response = s3_client.get_object(Bucket=bucket, Key=source_pdf_key)
        pdf_bytes = response['Body'].read()
        
        # Create annotated image
        bbox = grounding_info.get('box', {})
        url = create_annotated_image_from_pdf(
            pdf_bytes=pdf_bytes,
            page_num=page_num,
            bounding_boxes=[bbox],
            output_s3_key=annotation_key,
            s3_client=s3_client,
            bucket=bucket,
            chunk_type=chunk_type
        )
        
        return url
        
    except Exception as e:
        print(f"Error processing annotation: {e}")
        return None


def extract_chunk_id_from_markdown(markdown_text: str) -> Optional[str]:
    """
    Extract chunk ID from markdown text containing anchor tags
    
    Args:
        markdown_text: Markdown text with anchor tags like <a id="chunk_123"></a>
    
    Returns:
        Chunk ID or None if not found
    """
    import re
    
    # Look for anchor tags with IDs
    pattern = r'<a id=["\'](.*?)["\']></a>'
    match = re.search(pattern, markdown_text)
    
    if match:
        return match.group(1)
    
    return None


