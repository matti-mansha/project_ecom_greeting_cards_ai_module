from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

from ai_module.utils.log_config import setup_logging
import logging

# Set up logging
setup_logging()

# Conversion utility
def mm_to_pixels(mm, dpi=300):
    """Convert millimeters to pixels at given DPI"""
    pixels = int((mm / 25.4) * dpi)
    return pixels

# Image creation
def create_base_image(width_mm=127, height_mm=177.8, dpi=300):
    """Create a blank white image with specified dimensions in mm"""
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    logging.info(f"Creating base image: {width_px}x{height_px} pixels ({width_mm}mm x {height_mm}mm)")
    return Image.new('RGB', (width_px, height_px), color='white')

# Font handling
def get_font(font_name="wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf", size=100):
    """Load a font with specified size and fallback to default"""
    try:
        font = ImageFont.truetype(font_name, size)
        return font
    except Exception as e:
        logging.error(f"Failed to load font '{font_name}': {e}. Using default font")
        return ImageFont.load_default()

# Text drawing with optimized sizing and poem handling
def draw_letter_content(image, greeting, body, signoff, start_x=0):
    """Draw letter content with 15% margins, sign-off right-aligned with newlines, in (23, 89, 141) color"""
    draw = ImageDraw.Draw(image)
    margin_percent = 0.15  # 15% margin
    min_font_size = 10
    max_font_size = 1000
    line_spacing_factor = 1.4
    text_color = (23, 89, 141)  # RGB color
    
    # Calculate margins in pixels relative to the right half
    width_margin = int(image.width * margin_percent / 2)  # Half the total width for right side
    height_margin = int(image.height * margin_percent)
    max_width = (image.width // 2) - (2 * width_margin)  # Right half minus margins
    usable_height = image.height - (2 * height_margin)
    logging.info(f"Width margin: {width_margin}px, Height margin: {height_margin}px")
    logging.info(f"Max text width: {max_width}px, Usable height: {usable_height}px")
    
    # Check if body is a poem (more than 2 newlines)
    new_line_count = body.count('\n')
    is_poem = new_line_count > 2
    logging.info(f"Body has {new_line_count} newlines. Is poem: {is_poem}")
    
    # Helper function to get text metrics
    def get_text_metrics(text, font, max_width, is_poem=False, right_align=False):
        if is_poem or right_align:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
        else:
            lines = []
            words = text.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if draw.textlength(test_line, font=font) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
        
        max_line_width = max((draw.textlength(line, font=font) for line in lines), default=0)
        fits_width = max_line_width <= max_width
        
        if is_poem:
            positions = [(max_width - draw.textlength(line, font=font)) / 2 + start_x + width_margin if line else start_x + width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        elif right_align:
            positions = [max_width - draw.textlength(line, font=font) + start_x + width_margin if line else start_x + width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        return lines, len(lines), [start_x + width_margin] * len(lines), fits_width  # Left-aligned with margin

    # Binary search for optimal font size
    def find_optimal_font_size(greeting, body, signoff, min_size, max_size):
        left, right = min_size, max_size
        optimal_size = min_size
        
        while left <= right:
            mid = (left + right) // 2
            font = get_font("wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf", mid)
            line_spacing = int(mid * line_spacing_factor)
            
            greeting_lines, greeting_count, _, _ = get_text_metrics(greeting, font, max_width)
            body_lines, body_count, _, body_fits = get_text_metrics(body, font, max_width, is_poem)
            signoff_lines, signoff_count, _, _ = get_text_metrics(signoff, font, max_width, right_align=True)
            
            total_lines = greeting_count + body_count + signoff_count + 2
            total_height = total_lines * line_spacing
            
            logging.info(f"Testing font size {mid}: Total lines: {total_lines}, Height: {total_height}px, "
                  f"Body fits width: {body_fits}")
            
            if total_height <= usable_height and body_fits:
                optimal_size = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return optimal_size

    # Find optimal font size
    font_size = find_optimal_font_size(greeting, body, signoff, min_font_size, max_font_size)
    font = get_font("wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf", font_size)
    line_spacing = int(font_size * line_spacing_factor)
    logging.info(f"Optimal font size selected: {font_size}")
    
    # Get final text metrics
    greeting_lines, greeting_count, greeting_x_positions, _ = get_text_metrics(greeting, font, max_width)
    body_lines, body_count, body_x_positions, _ = get_text_metrics(body, font, max_width, is_poem)
    signoff_lines, signoff_count, signoff_x_positions, _ = get_text_metrics(signoff, font, max_width, right_align=True)
    
    # Calculate total content height and center it
    total_lines = greeting_count + body_count + signoff_count + 2
    total_height = total_lines * line_spacing
    start_y = height_margin + (usable_height - total_height) // 2
    logging.info(f"Total content height: {total_height}px, Starting y-position: {start_y}px")
    
    # Draw the text
    y_pos = start_y
    logging.info("Drawing greeting")
    for i, line in enumerate(greeting_lines):
        draw.text((greeting_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing  # Gap
    logging.info("Drawing body" + (" (centered)" if is_poem else ""))
    for i, line in enumerate(body_lines):
        draw.text((body_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing  # Gap
    logging.info("Drawing sign-off (right-aligned)")
    for i, line in enumerate(signoff_lines):
        draw.text((signoff_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    return image

def create_letter_png_with_blank_page(greeting, body, signoff, output_path="output-page-02.png", width_mm=127, height_mm=177.8, dpi=300):
    """Create a PNG letter with a blank page on the left and dotted line in between"""
    # Double the width to accommodate the blank page on the left
    total_width_mm = width_mm * 2
    total_width_px = mm_to_pixels(total_width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    
    # Create a blank image with double width
    img = Image.new('RGB', (total_width_px, height_px), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a dotted line in the middle
    mid_x = total_width_px // 2
    dash_length = 10
    gap_length = 10
    y = 0
    while y < height_px:
        draw.line([(mid_x, y), (mid_x, y + dash_length)], fill='black', width=1)
        y += dash_length + gap_length
    
    # Draw the letter content on the right half
    img = draw_letter_content(img, greeting, body, signoff, start_x=mid_x)
    img.save(output_path, "PNG")
    return output_path


def concatenate_images(local_path, url, output_path="concatenated-output-page-01.png", width_mm=127, height_mm=177.8, dpi=300):
    """
    Concatenate two images (local last page on left, URL thumbnail on right) with a dotted line between.
    
    :param local_path: Path to the local image file (last page)
    :param url: URL to the remote image (thumbnail)
    :param output_path: Path to save the concatenated image
    :param width_mm: Width of each image in millimeters
    :param height_mm: Height of each image in millimeters
    :param dpi: Dots per inch for resolution
    """
    # Convert dimensions to pixels
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    total_width_px = width_px * 2  # Double width for side-by-side layout
    
    # Load the local image (last page)
    try:
        last_page_img = Image.open(local_path).convert('RGB')
        # Resize to match specified dimensions
        last_page_img = last_page_img.resize((width_px, height_px), Image.Resampling.LANCZOS)
        logging.info(f"Loaded and resized local image from {local_path} to {width_px}x{height_px}")
    except Exception as e:
        logging.error(f"Error loading local image from {local_path}: {e}")
        return None
    
    # Load the image from URL (thumbnail)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        thumbnail_img = Image.open(BytesIO(response.content)).convert('RGB')
        # Resize to match specified dimensions
        thumbnail_img = thumbnail_img.resize((width_px, height_px), Image.Resampling.LANCZOS)
        logging.info(f"Loaded and resized image from URL {url} to {width_px}x{height_px}")
    except Exception as e:
        logging.error(f"Error loading image from URL {url}: {e}")
        return None
    
    # Create a new blank image with double width
    concatenated_img = Image.new('RGB', (total_width_px, height_px), color='white')
    
    # Paste the last page on the left
    concatenated_img.paste(last_page_img, (0, 0))
    
    # Paste the thumbnail on the right
    concatenated_img.paste(thumbnail_img, (width_px, 0))
    
    # Draw a dotted line in the middle
    draw = ImageDraw.Draw(concatenated_img)
    mid_x = width_px  # Middle point between the two images
    dash_length = 10
    gap_length = 10
    y = 0
    while y < height_px:
        draw.line([(mid_x, y), (mid_x, y + dash_length)], fill='black', width=1)
        y += dash_length + gap_length
    
    # Save the concatenated image
    try:
        concatenated_img.save(output_path, "PNG")
        logging.info(f"Created {output_path} with dimensions {total_width_px}x{height_px} pixels "
          f"({width_mm * 2}mm x {height_mm}mm at {dpi} DPI)")
    except Exception as e:
        logging.error(f"Error saving concatenated image to {output_path}: {e}")
        return None
    
    return output_path


def draw_letter_content_png(image, greeting, body, signoff):
    """Draw letter content with 15% margins, sign-off right-aligned with newlines, in (23, 89, 141) color"""
    draw = ImageDraw.Draw(image)
    margin_percent = 0.15  # 15% margin (corrected from 0.1 in your code to match request)
    min_font_size = 10
    max_font_size = 1000
    line_spacing_factor = 1.4
    text_color = (23, 89, 141)  # RGB color
    
    # Calculate margins in pixels
    width_margin = int(image.width * margin_percent)
    height_margin = int(image.height * margin_percent)
    max_width = image.width - (2 * width_margin)
    usable_height = image.height - (2 * height_margin)
    logging.info(f"Width margin: {width_margin}px, Height margin: {height_margin}px")
    logging.info(f"Max text width: {max_width}px, Usable height: {usable_height}px")
    
    # Check if body is a poem (more than 2 newlines)
    new_line_count = body.count('\n')
    is_poem = new_line_count > 2
    logging.info(f"Body has {new_line_count} newlines. Is poem: {is_poem}")
    
    # Helper function to get text metrics
    def get_text_metrics(text, font, max_width, is_poem=False, right_align=False):
        if is_poem or right_align:
            # Split by newlines for poems and sign-off to preserve line breaks
            lines = [line.strip() for line in text.split('\n') if line.strip()]
        else:
            # Wrap text for non-poems
            lines = []
            words = text.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if draw.textlength(test_line, font=font) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
        
        max_line_width = max((draw.textlength(line, font=font) for line in lines), default=0)
        fits_width = max_line_width <= max_width
        
        if is_poem:
            positions = [(max_width - draw.textlength(line, font=font)) / 2 + width_margin if line else width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        elif right_align:
            positions = [max_width - draw.textlength(line, font=font) + width_margin if line else width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        return lines, len(lines), [width_margin] * len(lines), fits_width  # Left-aligned with margin

    # Binary search for optimal font size
    def find_optimal_font_size(greeting, body, signoff, min_size, max_size):
        left, right = min_size, max_size
        optimal_size = min_size
        
        while left <= right:
            mid = (left + right) // 2
            font = get_font("wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf", mid)
            line_spacing = int(mid * line_spacing_factor)
            
            greeting_lines, greeting_count, _, _ = get_text_metrics(greeting, font, max_width)
            body_lines, body_count, _, body_fits = get_text_metrics(body, font, max_width, is_poem)
            signoff_lines, signoff_count, _, _ = get_text_metrics(signoff, font, max_width, right_align=True)
            
            total_lines = greeting_count + body_count + signoff_count + 2
            total_height = total_lines * line_spacing
            
            logging.info(f"Testing font size {mid}: Total lines: {total_lines}, Height: {total_height}px, "
                  f"Body fits width: {body_fits}")
            
            if total_height <= usable_height and body_fits:
                optimal_size = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return optimal_size
    
    # Find optimal font size
    font_size = find_optimal_font_size(greeting, body, signoff, min_font_size, max_font_size)
    font = get_font("wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf", font_size)
    line_spacing = int(font_size * line_spacing_factor)
    logging.info(f"Optimal font size selected: {font_size}")
    
    # Get final text metrics
    greeting_lines, greeting_count, greeting_x_positions, _ = get_text_metrics(greeting, font, max_width)
    body_lines, body_count, body_x_positions, _ = get_text_metrics(body, font, max_width, is_poem)
    signoff_lines, signoff_count, signoff_x_positions, _ = get_text_metrics(signoff, font, max_width, right_align=True)
    
    # Calculate total content height and center it
    total_lines = greeting_count + body_count + signoff_count + 2
    total_height = total_lines * line_spacing
    start_y = height_margin + (usable_height - total_height) // 2
    logging.info(f"Total content height: {total_height}px, Starting y-position: {start_y}px")
    
    # Draw the text
    y_pos = start_y
    logging.info("Drawing greeting")
    for i, line in enumerate(greeting_lines):
        draw.text((greeting_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing  # Gap
    logging.info("Drawing body" + (" (centered)" if is_poem else ""))
    for i, line in enumerate(body_lines):
        draw.text((body_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing  # Gap
    logging.info("Drawing sign-off (right-aligned)")
    for i, line in enumerate(signoff_lines):
        draw.text((signoff_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    return image

def create_letter_png(file_name, greeting, body, signoff, 
                     width_mm=127, height_mm=177.8, dpi=300):
    """Create a PNG letter with 15% margins, right-aligned sign-off with newlines, in custom color"""
    img = create_base_image(width_mm, height_mm, dpi)
    img = draw_letter_content_png(img, greeting, body, signoff)
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    img.save(file_name, "PNG")
    logging.info(f"Created {file_name} with dimensions {width_px}x{height_px} pixels "
          f"({width_mm}mm x {height_mm}mm at {dpi} DPI)")
    
    return file_name