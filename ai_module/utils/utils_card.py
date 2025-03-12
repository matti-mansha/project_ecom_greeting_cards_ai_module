from ai_module.utils.utils import load_config
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from ai_module.utils.letter_generator import create_letter_png_with_blank_page, concatenate_images
from reportlab.pdfgen import canvas
from ai_module.utils.letter_generator import create_letter_png
import logging
import os


config = load_config()

def upload_to_aws(local_file, bucket_name, s3_file_prefix="generated-cards/"):
    """
    Function to upload a file to an S3 bucket with a unique S3 object name, inside a specified folder,
    and return the S3 URL of the uploaded file.
    :param local_file: File to upload
    :param bucket_name: Bucket to upload to
    :param s3_file_prefix: Prefix (folder path) for the S3 object name. Defaults to "generated-cards/"
    :return: The URL of the uploaded file on S3 if successful, otherwise None
    """
    # Create an S3 client
    s3 = boto3.client('s3',
                    aws_access_key_id = config['AWS']['aws_access_key_id'],
                    aws_secret_access_key=config['AWS']['aws_secret_access_key']
                    )

    # Generate a unique file name using UUID
    unique_file_name = f"{uuid.uuid4()}.pdf"
    # Prepend the folder name to the file name
    s3_file = f"{s3_file_prefix}{unique_file_name}"

    try:
        # Upload the file
        s3.upload_file(local_file, bucket_name, s3_file)
        logging.info(f"Upload Successful: {s3_file} to {bucket_name}")

        # Construct the file URL
        bucket_location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        if bucket_location:
            s3_url = f"https://{bucket_name}.s3-{bucket_location}.amazonaws.com/{s3_file}"
        else:
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file}"

        return s3_url
    except FileNotFoundError:
        logging.error("The file was not found")
        return None
    except NoCredentialsError:
        logging.error("Credentials not available")
        return None


def upload_to_aws_png(local_file, bucket_name, s3_file_prefix="generated-cards-png/"):
    """
    Function to upload a file to an S3 bucket with a unique S3 object name, inside a specified folder,
    and return the S3 URL of the uploaded file.
    :param local_file: File to upload
    :param bucket_name: Bucket to upload to
    :param s3_file_prefix: Prefix (folder path) for the S3 object name. Defaults to "generated-cards/"
    :return: The URL of the uploaded file on S3 if successful, otherwise None
    """
    local_file_path = os.path.join(local_file)  # Adjust path as needed
    if os.path.exists(local_file_path):
        logging.info(f"Ready to upload {local_file_path}")
    else:
        logging.error(f"File not found: {local_file_path}")
        return None
    
    # Create an S3 client
    s3 = boto3.client('s3',
                    aws_access_key_id = config['AWS']['aws_access_key_id'],
                    aws_secret_access_key=config['AWS']['aws_secret_access_key']
                    )

    # Generate a unique file name using UUID
    unique_file_name = f"{uuid.uuid4()}.png"
    # Prepend the folder name to the file name
    s3_file = f"{s3_file_prefix}{unique_file_name}"

    try:
        
        # Upload the file
        s3.upload_file(local_file_path, bucket_name, s3_file)
        logging.info(f"Upload Successful: {s3_file} to {bucket_name}")

        # Construct the file URL
        bucket_location = s3.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        if bucket_location:
            s3_url = f"https://{bucket_name}.s3-{bucket_location}.amazonaws.com/{s3_file}"
        else:
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file}"

        return s3_url
    except FileNotFoundError:
        logging.error("The file was not found")
        return None
    except NoCredentialsError:
        logging.error("Credentials not available")
        return None


def pngs_to_pdf(png1_path, png2_path, output_pdf="output.pdf", width_mm=127 * 2, height_mm=177.8):
    """
    Combine two PNG images into a PDF with each image on a separate page.
    
    :param png1_path: Path to the first PNG image (Page 1, e.g., last page)
    :param png2_path: Path to the second PNG image (Page 2, e.g., thumbnail)
    :param output_pdf: Path to save the output PDF
    :param width_mm: Width of each page in millimeters
    :param height_mm: Height of each page in millimeters
    """
    # Convert dimensions from mm to points (1 mm = 2.83464567 points)
    width_pt = width_mm * 2.83464567
    height_pt = height_mm * 2.83464567
    
    # Calculate pixel dimensions for reference
    dpi = 300  # Assuming 300 DPI for informational purposes
    width_px = int((width_mm / 25.4) * dpi)
    height_px = int((height_mm / 25.4) * dpi)
    logging.info(f"Each page size: {width_px}x{height_px} pixels ({width_mm}mm x {height_mm}mm)")
    logging.info(f"PDF page size: {width_pt}x{height_pt} points ({width_mm}mm x {height_mm}mm)")
    
    # Check if input files exist
    if not os.path.exists(png1_path):
        logging.error(f"Error: {png1_path} does not exist")
        return None
    if not os.path.exists(png2_path):
        logging.error(f"Error: {png2_path} does not exist")
        return None
    
    # Create PDF
    c = canvas.Canvas(output_pdf, pagesize=(width_pt, height_pt))
    
    # Page 1: Add first image (e.g., last page)
    c.drawImage(png1_path, 0, 0, width_pt, height_pt)
    c.showPage()
    
    # Page 2: Add second image (e.g., thumbnail)
    c.drawImage(png2_path, 0, 0, width_pt, height_pt)
    c.showPage()
    
    # Save the PDF
    c.save()
    
    logging.info(f"Created PDF: {output_pdf} with 2 pages, each {width_pt}x{height_pt} points "
          f"({width_mm}mm x {height_mm}mm)")
    return output_pdf

def generate_card_pdf(greeting, body, signoff, thumbnail, last_page, final_filename="output.pdf", bucket_name = config['AWS']['bucket_name']):
    """
    Generates a custom greeting card in PDF format with a given greeting, body, and signoff text,
    includes a thumbnail image, and allows for custom DPI and final filename specifications.
    The process involves creating an intermediate PDF, converting it to images, and then compiling
    everything into the final PDF file.
    
    :param greeting: The greeting text for the card.
    :param body: The body text for the card.
    :param signoff: The signoff text for the card.
    :param thumbnail: The thumbnail image for the card.
    :param final_filename: The name of the final PDF file. Defaults to "output.pdf".
    :param last_page: URL to an image for the last page of the PDF. Defaults to a specific image.
    :param bucket_name: The name of the S3 bucket to upload the final PDF to.
    """
    
    try:
        # Check if last_page is a valid path or URL
        if not last_page or (not os.path.exists(last_page)):
            last_page = "https://tobre-cards.s3.us-east-2.amazonaws.com/images/0f0d6ee0-4dfe-4712-9621-1ed07753397f-last%20page.png"
            logging.info(f"Last page is not a valid path or URL. Using default last page: {last_page}")
        else:
            last_page = last_page
            logging.info(f"Last page is a valid path or URL: {last_page}")
    except:
        last_page = "https://tobre-cards.s3.us-east-2.amazonaws.com/images/0f0d6ee0-4dfe-4712-9621-1ed07753397f-last%20page.png"
        logging.info(f"Last page is not a valid path or URL. Using default last page: {last_page}")


    output_page_02 = create_letter_png_with_blank_page(greeting, body, signoff, output_path="output-page-02.png", width_mm=127, height_mm=177.8, dpi=300)
    output_page_01 = concatenate_images(last_page, thumbnail, output_path="output-page-01.png", width_mm=127, height_mm=177.8, dpi=300)

    final_filename = pngs_to_pdf(output_page_01, output_page_02, output_pdf="output.pdf", width_mm=127 * 2, height_mm=177.8)

    # Define the file you want to upload
    local_file = final_filename

    # Call the function to upload without specifying the s3_file name
    uploaded = upload_to_aws(local_file, bucket_name)

    # Cleanup: Remove the intermediate PDF used for image conversion
    if os.path.exists(final_filename):
        os.remove(final_filename)
        logging.info(f"The file {final_filename} has been deleted.")
    else:
        logging.info(f"The file {final_filename} does not exist.")

    return uploaded


def generate_card_png(greeting, body, signoff, final_filename="output_images/output.png", last_page="https://tobre-cards.s3.us-east-2.amazonaws.com/images/0f0d6ee0-4dfe-4712-9621-1ed07753397f-last%20page.png", bucket_name = config['AWS']['bucket_name']):
    """
    Generates a custom greeting card in PDF format with a given greeting, body, and signoff text,
    includes a thumbnail image, and allows for custom DPI and final filename specifications.
    The process involves creating an intermediate PDF, converting it to images, and then compiling
    everything into the final PDF file.
    
    :param greeting: The greeting text for the card.
    :param body: The body text for the card.
    :param signoff: The signoff text for the card.
    :param final_filename: The name of the final PDF file. Defaults to "output.pdf".
    :param last_page: URL to an image for the last page of the PDF. Defaults to a specific image.
    :param bucket_name: The name of the S3 bucket to upload the final PDF to.
    """

    final_filename1 = create_letter_png(final_filename, greeting, body, signoff, width_mm=127, height_mm=177.8, dpi=300)


    # Define the file you want to upload
    logging.info(f"The of final filename {final_filename1}.")
    local_file = final_filename

    # Call the function to upload without specifying the s3_file name
    uploaded = upload_to_aws_png(local_file, bucket_name)


    return uploaded, last_page