# class PDF(FPDF):
#     unifontsubset = False  # Add this attribute if it's missing
    
#     def header(self):
#         # This method can be used to create headers
#         pass

#     def dotted_line(self, x1, y1, x2, y2):
#         # Draws a straight dotted line between x1,y1 and x2,y2
#         self.set_line_width(0.1)
#         self.set_draw_color(0, 0, 0)
#         if x1 == x2:  # Vertical line
#             while y1 < y2:
#                 self.line(x1, y1, x1, y1 + 1)
#                 y1 += 3
#         elif y1 == y2:  # Horizontal line
#             while x1 < x2:
#                 self.line(x1, y1, x1 + 1, y1)
#                 x1 += 3


# def text_to_pdf_final(greeting, body, signoff, width_mm = 101.6, height_mm = 142.24, filename="output.pdf"):
#     logging.info("Starting PDF creation: width=%smm, height=%smm", width_mm, height_mm)
#     logging.info("Content lengths - Greeting: %s chars, Body: %s chars, Signoff: %s chars", 
#                  len(greeting), len(body), len(signoff))
    
#     # Initialize PDF with dynamic margins
#     pdf = PDF(unit='mm', format=(width_mm, height_mm))
#     left_margin = 0  # Fixed left margin
#     top_margin = 0  # Fixed top margin
#     right_margin = left_margin  # Right margin equals left margin for symmetry
#     # logging.info("Margins set - Left: %s, Top: %s, Right: %s", left_margin, top_margin, right_margin)

#     # Then, set the margins for the content page
#     pdf.set_margins(left_margin, top_margin, right_margin)
#     # Add the content page
#     pdf.add_page()
#     # logging.info("Page added with margins")

#     # Adaptive font size settings based on body length
#     font_size = 200
#     min_font_size = 10  # Minimum font size
#     padding = 0
#     # logging.info("Initial font size: %s, Minimum font size: %s", font_size, min_font_size)
    
#     # Add font
#     pdf.add_font('Wilson', '', r'wilson-p4chbsdco3fw3f363hr4acd9fr (1).ttf', uni=True)
#     pdf.set_font('Wilson', '', font_size)
#     # logging.info("Wilson font added and set to size %s", font_size)

#     # Determine the longest line in the body text if it is a poem
#     max_line_width = 0
#     new_line_count = body.count('\n')
#     logging.info("Body contains %s newlines", new_line_count)
    
#     if new_line_count > 2:
#         lines = body.split('\n')
#         line_widths = [pdf.get_string_width(line) for line in lines]
#         max_line_width = max(line_widths)
#         # logging.info("Multiple lines detected. Line widths: %s", line_widths)
#         # logging.info("Max line width: %s", max_line_width)

#     content_width = (width_mm) - (left_margin + right_margin + 2 * padding)
#     # logging.info("Available content width: %s", content_width)

#     # Adjust the font size if the longest line of the poem doesn't fit
#     is_poem = False
#     if new_line_count > 2 and max_line_width > content_width + 10:
#         # logging.info("POEM detected - adjusting font size for poem formatting")
#         is_poem = True
#         initial_poem_font = font_size
#         while font_size > min_font_size and max_line_width > content_width:
#             font_size -= 1
#             pdf.set_font('Wilson', '', font_size)
#             max_line_width = max(pdf.get_string_width(line) for line in lines)
#             logging.info("Reducing font size to %s, new max line width: %s", font_size, max_line_width)
#         # 
#         # logging.info("Final poem font size: %s (reduced from %s)", font_size, initial_poem_font)

#     # Try fitting the content on one page by adjusting font size
#     initial_content_font = font_size
#     total_height_steps = []
    
#     while font_size >= min_font_size:
#         pdf.set_font('Wilson', '', font_size)
#         pdf.set_auto_page_break(auto=False)  # Disable automatic page breaking

#         # Calculate total height of the content
#         total_height = 0
#         heights = []
        
#         for i, text in enumerate([greeting, body, signoff]):
#             text_name = ["greeting", "body", "signoff"][i]
#             text_width = pdf.get_string_width(text)
#             estimated_lines = text_width / content_width
#             text_height = estimated_lines * font_size + padding
#             heights.append(text_height)
#             total_height += text_height
#             # logging.info("%s - Width: %s, Est. lines: %.2f, Height: %.2f", 
#             #              text_name, text_width, estimated_lines, text_height)
        
#         total_height_steps.append(f"Font {font_size}: total height = {total_height}mm")
#         # logging.info("With font size %s - Total height: %s, Available height: %s", 
#         #              font_size, total_height, height_mm)

#         if total_height <= height_mm:
#             # logging.info("Content fits with font size %s", font_size)
#             break  # Content fits within one page, break the loop
        
#         font_size -= 1  # Decrease font size and try again
#         # logging.info("Reducing font size to %s and recalculating", font_size)

#     # logging.info("Font size adjustment steps:\n%s", "\n".join(total_height_steps))
#     # logging.info("Final font Size = %s (reduced from %s)", font_size, initial_content_font)
    
#     # Apply the determined font size for all text sections
#     pdf.set_font('Wilson', '', font_size)

#     # Greeting text
#     pdf.set_text_color(30, 64, 175)
#     logging.info("Text color set to RGB(30, 64, 175)")
    
#     pdf.set_xy(0, 0)
#     logging.info("Position set to (0, 0) for greeting")
    
#     pdf.multi_cell(0, 8, greeting, align='L')
#     greeting_end_y = pdf.get_y()
#     # logging.info("Greeting rendered, ending at y-position: %s", greeting_end_y)
    
#     pdf.ln(10)  # Add a line space before the body
#     logging.info("Added 10mm line space, new y-position: %s", pdf.get_y())

#     if is_poem:
#         # Body text for poem (centered)
#         logging.info("Rendering poem body with centered alignment")
#         pdf.set_xy(left_margin + padding, pdf.get_y() + padding)
#         logging.info("Body position set to (%s, %s)", left_margin + padding, pdf.get_y())
        
#         pdf.multi_cell(content_width, 8, body, align='C')
#         body_end_y = pdf.get_y()
#         logging.info("Body rendered (centered), ending at y-position: %s", body_end_y)
#     else:
#         # Body text (left-aligned)
#         logging.info("Rendering regular body with left alignment")
#         pdf.set_xy(left_margin + padding, pdf.get_y() + padding)
#         logging.info("Body position set to (%s, %s)", left_margin + padding, pdf.get_y())
        
#         pdf.multi_cell(content_width, 8, body, align='L')
#         body_end_y = pdf.get_y()
#         logging.info("Body rendered (left-aligned), ending at y-position: %s", body_end_y)

#     # Signoff text
#     pdf.ln(10)  # Add a line space before the signoff
#     logging.info("Added 10mm line space before signoff, new y-position: %s", pdf.get_y())
    
#     signoff_width = pdf.get_string_width(signoff) + padding
#     signoff_x = width_mm - signoff_width - right_margin - (2 * padding)
#     pdf.set_x(signoff_x)
#     logging.info("Signoff width: %s, positioned at x: %s", signoff_width, signoff_x)
    
#     pdf.multi_cell(signoff_width, 8, signoff, align='R')
#     signoff_end_y = pdf.get_y()
#     logging.info("Signoff rendered (right-aligned), ending at y-position: %s", signoff_end_y)

#     # Check if content fits
#     if signoff_end_y > height_mm:
#         logging.warning("WARNING: Content may have overflowed! Final y-position (%s) exceeds page height (%s)", 
#                         signoff_end_y, height_mm)
#     else:
#         logging.info("Content fits within page (used %s of %s mm)", signoff_end_y, height_mm)

#     # Output the PDF
#     pdf.output(filename)
#     logging.info("PDF successfully output to %s", filename)
    
#     return pdf.get_y(), filename


# def card_pdf_maker(last_page, thumbnail, center_img, filename="output.pdf"):
    
#     width_mm = 2 * 5 * 25.4  # Double Width in millimeters for side by side layout
#     height_mm = 7 * 25.4  # Height in millimeters

#     # Use Pillow to open the image and get its size
#     with Image.open(center_img) as img:
#         px_width, px_height = img.size
#         dpi = img.info.get('dpi', (300, 300))[0]  # Default to 72 DPI if not found
#         image_width_mm = (px_width / dpi) * 25.4  # Convert pixels to millimeters
#         image_height_mm = (px_height / dpi) * 25.4

#     pdf = PDF(unit='mm', format=(width_mm, height_mm))
#     pdf.set_auto_page_break(auto=False)  # Disable automatic page breaking
#     pdf.add_page()

#     # Draw the dotted line down the center
#     center_line_x = width_mm / 2
#     pdf.dotted_line(center_line_x, 0, center_line_x, height_mm)
    
#     # Calculate the position to center the image in the right half
#     center_image_x = center_line_x + ((width_mm / 2 - image_width_mm) / 2)
#     center_image_y = (height_mm - image_height_mm) / 2

#     # Place the center image on the right side of the first page, centered within the right half
#     pdf.image(center_img, x=center_image_x, y=center_image_y, w=image_width_mm, h=image_height_mm)

#     # Output the PDF
#     # Add a new page for the images
#     pdf.add_page()

#     # Calculate the dimensions and position for the images
#     image_width_mm = 127  # 5 inches in mm
#     image_height_mm = 177.8  # 7 inches in mm
#     center_line_x = width_mm / 2

#     # Place the first image on the left side
#     pdf.image(last_page, x=0, y=0, w=image_width_mm, h=image_height_mm)

#     # Place the second image on the right side, adjacent to the first
#     pdf.image(thumbnail, x=center_line_x, y=0, w=image_width_mm, h=image_height_mm)

#     # Draw a dotted line down the center of the second page
#     pdf.dotted_line(center_line_x, 0, center_line_x, height_mm)

#     # Output the PDF
#     pdf.output(filename)


# def convert_pdf_to_png(pdf_file, output_folder='output_images'):
#     # Create output folder if it doesn't exist
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     # Convert the PDF to a list of images at 300 DPI
#     images = convert_from_path(pdf_file, dpi=300)

#     # Save each page as an image
#     image_paths = []
#     for i, image in enumerate(images):
#         image_path = os.path.join(output_folder, f'generated.png')
#         image.save(image_path, 'PNG')
#         image_paths.append(image_path)
#         logging.info(f'Saved {image_path}')

#     # Optionally, clean up the temporary PDF file
#     os.remove(pdf_file)
    
#     return image_paths

# def card_pdf_maker_writing(center_img, filename="output.pdf"):
#     width_mm = 5 * 25.4  # Double Width in millimeters for side by side layout
#     height_mm = 7 * 25.4  # Height in millimeters

#     # Use Pillow to open the image and get its size
#     with Image.open(center_img) as img:
#         px_width, px_height = img.size
#         dpi = img.info.get('dpi', (300, 300))[0]  # Default to 72 DPI if not found
#         image_width_mm = (px_width / dpi) * 25.4  # Convert pixels to millimeters
#         image_height_mm = (px_height / dpi) * 25.4

#     pdf = PDF(unit='mm', format=(width_mm, height_mm))
#     pdf.set_auto_page_break(auto=False)  # Disable automatic page breaking
#     pdf.add_page()

#     # Draw the dotted line down the center
#     center_line_x = 0
#     # pdf.dotted_line(center_line_x, 0, center_line_x, height_mm)
    
#     # Calculate the position to center the image in the right half
#     center_image_x = center_line_x + ((width_mm - image_width_mm) / 2)
#     center_image_y = (height_mm - image_height_mm) / 2

#     # Place the center image on the right side of the first page, centered within the right half
#     pdf.image(center_img, x=center_image_x, y=center_image_y, w=image_width_mm, h=image_height_mm)

#     # Save the PDF temporarily
#     temp_pdf_path = filename
#     pdf.output(temp_pdf_path)

#     # Convert the PDF to PNG
#     convert_pdf_to_png(temp_pdf_path)


# def generate_card_pdf_old(greeting, body, signoff, thumbnail, last_page="https://tobre-cards.s3.us-east-2.amazonaws.com/images/0f0d6ee0-4dfe-4712-9621-1ed07753397f-last%20page.png", dpi=300, final_filename="output.pdf", margined_width_mm=101.6, margined_height_mm=142.24, center_img="page_0.png", center_filename="center_portion.pdf", bucket_name = config['AWS']['bucket_name']):
#     """
#     Generates a custom greeting card in PDF format with a given greeting, body, and signoff text,
#     includes a thumbnail image, and allows for custom DPI and final filename specifications.
#     The process involves creating an intermediate PDF, converting it to images, and then compiling
#     everything into the final PDF file.
    
#     :param greeting: The greeting text for the card.
#     :param body: The body text for the card.
#     :param signoff: The signoff text for the card.
#     :param thumbnail: The thumbnail image for the card.
#     :param dpi: Dots Per Inch, for image quality in the final PDF. Defaults to 300.
#     :param final_filename: The name of the final PDF file. Defaults to "output.pdf".
#     :param last_page: URL to an image for the last page of the PDF. Defaults to a specific image.
#     :param margined_width_mm: The width of the PDF including margins, in millimeters.
#     :param margined_height_mm: The height of the PDF including margins, in millimeters.
#     :param center_img: The filename for the center image in the final PDF. Defaults to "page_0.png".
#     :param center_filename: The filename for the intermediate center portion PDF. Defaults to "center_portion.pdf".
#     """
    
#     # First, create a temporary PDF to calculate the necessary dimensions
#     y, filename = text_to_pdf_final(greeting, body, signoff, filename="temp_file.pdf")
#     if os.path.exists(filename):
#         os.remove(filename)  # Clean up the temporary file
#         logging.info(f"The file {filename} has been deleted.")
#     else:
#         logging.info(f"The file {filename} does not exist.")

#     # Generate the main content PDF with the specified dimensions
#     _, filename = text_to_pdf_final(greeting=greeting, body=body, signoff=signoff, width_mm=101.6, height_mm=float(y), filename="center_portion.pdf")

#     # Convert the PDF to high-quality images for further processing
#     images = convert_from_path(center_filename, dpi=dpi)
#     for i, image in enumerate(images):
#         image_path = f'page_{i}.png'
#         image.save(image_path, 'PNG')  # Save each PDF page as an image
#         logging.info(f"Page {i+1}: Width = {image.width}px, Height = {image.height}px")
        
#         # Note: The variable 'dpi_setting' is not defined in the original code snippet.
#         # Assuming it's meant to be the 'dpi' parameter for accurate calculations.
#         logging.info(f"Approx. Dimensions in mm (at {dpi} DPI): Width = {image.width / dpi * 25.4}mm, Height = {image.height / dpi * 25.4}mm")

#     # Cleanup: Remove the intermediate PDF used for image conversion
#     if os.path.exists(filename):
#         os.remove(filename)
#         logging.info(f"The file {filename} has been deleted.")
#     else:
#         logging.info(f"The file {filename} does not exist.")

#     # Combine all parts into the final PDF
#     card_pdf_maker(last_page, thumbnail, center_img, final_filename)

#     # Interchange the pages in the final PDF
#     pdf_reader = PdfReader(final_filename)
#     pdf_writer = PdfWriter()

#     # Swap the order of pages
#     if len(pdf_reader.pages) >= 2:
#         pdf_writer.add_page(pdf_reader.pages[1])
#         pdf_writer.add_page(pdf_reader.pages[0])

#         with open(final_filename, 'wb') as out_pdf:
#             pdf_writer.write(out_pdf)
#         logging.info("Pages have been swapped in the final PDF.")
#     else:
#         logging.error("The final PDF does not have enough pages to swap.")


#     # Define the file you want to upload
#     local_file = final_filename

#     # Call the function to upload without specifying the s3_file name
#     uploaded = upload_to_aws(local_file, bucket_name)

#     # Cleanup: Remove the intermediate PDF used for image conversion
#     if os.path.exists(final_filename):
#         os.remove(final_filename)
#         logging.info(f"The file {final_filename} has been deleted.")
#     else:
#         logging.info(f"The file {final_filename} does not exist.")

#     return uploaded


# def generate_card_png_old(greeting, body, signoff, dpi=300, final_filename="output.png", last_page="https://tobre-cards.s3.us-east-2.amazonaws.com/images/0f0d6ee0-4dfe-4712-9621-1ed07753397f-last%20page.png", margined_width_mm=101.6, margined_height_mm=142.24, center_img="page_0.png", center_filename="center_portion.pdf", bucket_name = config['AWS']['bucket_name']):
#     """
#     Generates a custom greeting card in PDF format with a given greeting, body, and signoff text,
#     includes a thumbnail image, and allows for custom DPI and final filename specifications.
#     The process involves creating an intermediate PDF, converting it to images, and then compiling
#     everything into the final PDF file.
    
#     :param greeting: The greeting text for the card.
#     :param body: The body text for the card.
#     :param signoff: The signoff text for the card.
#     :param dpi: Dots Per Inch, for image quality in the final PDF. Defaults to 300.
#     :param final_filename: The name of the final PDF file. Defaults to "output.pdf".
#     :param last_page: URL to an image for the last page of the PDF. Defaults to a specific image.
#     :param margined_width_mm: The width of the PDF including margins, in millimeters.
#     :param margined_height_mm: The height of the PDF including margins, in millimeters.
#     :param center_img: The filename for the center image in the final PDF. Defaults to "page_0.png".
#     :param center_filename: The filename for the intermediate center portion PDF. Defaults to "center_portion.pdf".
#     """
    
#     # First, create a temporary PDF to calculate the necessary dimensions
#     y, filename = text_to_pdf_final(greeting, body, signoff, filename="temp_file.pdf")
#     if os.path.exists(filename):
#         os.remove(filename)  # Clean up the temporary file
#         logging.info(f"The file {filename} has been deleted.")
#     else:
#         logging.info(f"The file {filename} does not exist.")

#     # Generate the main content PDF with the specified dimensions
#     _, filename = text_to_pdf_final(greeting=greeting, body=body, signoff=signoff, width_mm=101.6, height_mm=float(y), filename="center_portion.pdf")

#     # Convert the PDF to high-quality images for further processing
#     images = convert_from_path(center_filename, dpi=dpi)
#     for i, image in enumerate(images):
#         image_path = f'page_{i}.png'
#         image.save(image_path, 'PNG')  # Save each PDF page as an image
#         logging.info(f"Page {i+1}: Width = {image.width}px, Height = {image.height}px")
        
#         # Note: The variable 'dpi_setting' is not defined in the original code snippet.
#         # Assuming it's meant to be the 'dpi' parameter for accurate calculations.
#         logging.info(f"Approx. Dimensions in mm (at {dpi} DPI): Width = {image.width / dpi * 25.4}mm, Height = {image.height / dpi * 25.4}mm")

#     # Cleanup: Remove the intermediate PDF used for image conversion
#     if os.path.exists(filename):
#         os.remove(filename)
#         logging.info(f"The file {filename} has been deleted.")
#     else:
#         logging.info(f"The file {filename} does not exist.")

#     # Combine all parts into the final PDF
#     card_pdf_maker_writing(center_img, final_filename)

#     # Define the file you want to upload
#     logging.info(f"The of final filename {final_filename}.")
#     local_file = final_filename

#     # Call the function to upload without specifying the s3_file name
#     uploaded = upload_to_aws_png(local_file, bucket_name)

#     # Cleanup: Remove the intermediate PDF used for image conversion
#     if os.path.exists(final_filename):
#         os.remove(final_filename)
#         logging.info(f"The file {final_filename} has been deleted.")
#     else:
#         logging.info(f"The file {final_filename} does not exist.")

#     return uploaded, last_page