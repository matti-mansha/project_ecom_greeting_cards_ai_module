from PIL import Image, ImageDraw, ImageFont
import os

# Conversion utility
def mm_to_pixels(mm, dpi=300):
    pixels = int((mm / 25.4) * dpi)
    print(f"Converted {mm}mm to {pixels}px at {dpi} DPI")
    return pixels

# Image creation
def create_base_image(width_mm=127, height_mm=177.8, dpi=300):
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    print(f"Creating base image: {width_px}x{height_px} pixels ({width_mm}mm x {height_mm}mm)")
    return Image.new('RGB', (width_px, height_px), color='white')

# Font handling
def get_font(size=100):
    custom_font_path = "wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf"
    fallback_font = "arial.ttf"  # Common font as fallback
    
    if os.path.exists(custom_font_path):
        try:
            font = ImageFont.truetype(custom_font_path, size)
            print(f"Loaded custom font '{custom_font_path}' at size {size}")
            return font
        except Exception as e:
            print(f"Failed to load custom font '{custom_font_path}': {e}")
    
    try:
        font = ImageFont.truetype(fallback_font, size)
        print(f"Loaded fallback font '{fallback_font}' at size {size}")
        return font
    except Exception as e:
        print(f"Failed to load '{fallback_font}': {e}")
    
    print("Falling back to Pillow's default font")
    return ImageFont.load_default()

# Text drawing with optimized sizing and poem handling
def draw_letter_content(image, greeting, body, signoff):
    draw = ImageDraw.Draw(image)
    margin_percent = 0.15  # 15% margin
    min_font_size = 10
    max_font_size = 1000
    line_spacing_factor = 1.4
    text_color = (23, 89, 141)
    
    width_margin = int(image.width * margin_percent)
    height_margin = int(image.height * margin_percent)
    max_width = image.width - (2 * width_margin)
    usable_height = image.height - (2 * height_margin)
    print(f"Width margin: {width_margin}px, Height margin: {height_margin}px")
    print(f"Max text width: {max_width}px, Usable height: {usable_height}px")
    
    new_line_count = body.count('\n')
    is_poem = new_line_count > 2
    print(f"Body has {new_line_count} newlines. Is poem: {is_poem}")
    
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
            positions = [(max_width - draw.textlength(line, font=font)) / 2 + width_margin if line else width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        elif right_align:
            positions = [max_width - draw.textlength(line, font=font) + width_margin if line else width_margin 
                        for line in lines]
            return lines, len(lines), positions, fits_width
        return lines, len(lines), [width_margin] * len(lines), fits_width

    def find_optimal_font_size(greeting, body, signoff, min_size, max_size):
        left, right = min_size, max_size
        optimal_size = min_size
        
        while left <= right:
            mid = (left + right) // 2
            font = get_font(size=mid)
            line_spacing = int(mid * line_spacing_factor)
            
            greeting_lines, greeting_count, _, _ = get_text_metrics(greeting, font, max_width)
            body_lines, body_count, _, body_fits = get_text_metrics(body, font, max_width, is_poem)
            signoff_lines, signoff_count, _, _ = get_text_metrics(signoff, font, max_width, right_align=True)
            
            total_lines = greeting_count + body_count + signoff_count + 2
            total_height = total_lines * line_spacing
            
            print(f"Testing font size {mid}: Total lines: {total_lines}, Height: {total_height}px, "
                  f"Body fits width: {body_fits}")
            
            if total_height <= usable_height and body_fits:
                optimal_size = mid
                left = mid + 1
            else:
                right = mid - 1
        
        return optimal_size

    font_size = find_optimal_font_size(greeting, body, signoff, min_font_size, max_font_size)
    font = get_font(size=font_size)
    line_spacing = int(font_size * line_spacing_factor)
    print(f"Optimal font size selected: {font_size}")
    
    greeting_lines, greeting_count, greeting_x_positions, _ = get_text_metrics(greeting, font, max_width)
    body_lines, body_count, body_x_positions, _ = get_text_metrics(body, font, max_width, is_poem)
    signoff_lines, signoff_count, signoff_x_positions, _ = get_text_metrics(signoff, font, max_width, right_align=True)
    
    total_lines = greeting_count + body_count + signoff_count + 2
    total_height = total_lines * line_spacing
    start_y = height_margin + (usable_height - total_height) // 2
    print(f"Total content height: {total_height}px, Starting y-position: {start_y}px")
    
    y_pos = start_y
    print("Drawing greeting")
    for i, line in enumerate(greeting_lines):
        draw.text((greeting_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing
    print("Drawing body" + (" (centered)" if is_poem else ""))
    for i, line in enumerate(body_lines):
        draw.text((body_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    y_pos += line_spacing
    print("Drawing sign-off (right-aligned)")
    for i, line in enumerate(signoff_lines):
        draw.text((signoff_x_positions[i], y_pos), line, font=font, fill=text_color)
        y_pos += line_spacing
    
    return image

# Main function
def create_letter_png(file_name, greeting, body, signoff, width_mm=127, height_mm=177.8, dpi=300):
    img = create_base_image(width_mm, height_mm, dpi)
    img = draw_letter_content(img, greeting, body, signoff)
    width_px = mm_to_pixels(width_mm, dpi)
    height_px = mm_to_pixels(height_mm, dpi)
    img.save(f"{file_name}.png", "PNG")
    print(f"Created {file_name}.png with dimensions {width_px}x{height_px} pixels "
          f"({width_mm}mm x {height_mm}mm at {dpi} DPI)")

# Example usage
if __name__ == "__main__":
    create_letter_png(
        "long_letter",
        "Dear Brother,",
        "On your special day, embrace the joy and laughter. Wishing you a fantastic birthday filled with funny!",
        "Yours Sincerely,\nMatti"
    )