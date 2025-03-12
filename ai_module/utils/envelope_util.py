from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import json
import os
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
import logging
import configparser

def load_config():
    """
    Loads and returns the configuration from the config.ini file in the project root directory.
    """
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up two levels to the project root
    project_root = os.path.dirname(os.path.dirname(script_dir))

    # Construct the path to the config.ini file
    config_file_path = os.path.join(project_root, 'config.ini')

    # Initialize and read the config parser
    config = configparser.ConfigParser()
    config.read(config_file_path)

    return config

# Load configuration
config = load_config()

def setup_fonts(corinth_font_path, hello_mommy_font_path, aldo_font_path):
    """Register custom fonts."""
    pdfmetrics.registerFont(TTFont('CorinthTwo-Regular', corinth_font_path))
    pdfmetrics.registerFont(TTFont('HelloMommy', hello_mommy_font_path))
    pdfmetrics.registerFont(TTFont('Aldo', aldo_font_path))

def create_envelope(address, return_address, output_dir, fonts):
    """Create a single envelope PDF."""
    width, height = 7.25 * inch, 5.25 * inch
    file_path = os.path.join(output_dir, f"{address['Name'].replace(' ', '_')}.pdf")
    c = canvas.Canvas(file_path, pagesize=(width, height))

    c.setFillColorRGB(30/255, 64/255, 175/255)  # Blue color
    
    # Return address
    c.setFont(fonts['return']['font'], fonts['return']['size'])
    c.drawString(0.5 * inch, height - 0.75 * inch, return_address['name'])
    c.setFont(fonts['return_address']['font'], fonts['return_address']['size'])
    for i, line in enumerate(return_address['address']):
        c.drawString(0.5 * inch, height - (1 + i * 0.25) * inch, line)

    # Recipient address
    recipient_name = address['Name']
    recipient_address_lines = [
        address['Street'],
        f"{address['City']}, {address['State']} {address['ZIP']}"
    ]

    # Set font for recipient's name
    c.setFont(fonts['recipient']['font'], fonts['recipient']['size'])
    text_width = c.stringWidth(recipient_name, fonts['recipient']['font'], fonts['recipient']['size'])
    c.drawString((width - text_width) / 2, height / 2 + 0.1 * inch, recipient_name)

    # Set font for the rest of the address
    c.setFont(fonts['recipient_address']['font'], fonts['recipient_address']['size'])
    for i, line in enumerate(recipient_address_lines):
        text_width = c.stringWidth(line, fonts['recipient_address']['font'], fonts['recipient_address']['size'])
        c.drawString((width - text_width) / 2, height / 2 - 0.5 * inch - (i * 0.4 * inch), line)

    c.showPage()
    c.save()
    return file_path

def upload_to_aws(local_file, bucket_name, s3_file_prefix="envelopess/"):
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

def create_envelopes_from_json(json_data, return_address, output_dir, fonts):
    """Create envelopes from JSON input and upload to S3."""
    try:
        addresses = json.loads(json_data)
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON data: {e}")
        return []

    os.makedirs(output_dir, exist_ok=True)

    # Load AWS config
    config = configparser.ConfigParser()
    config.read('config.ini')
    bucket_name = config['AWS']['bucket_name']

    s3_links = []
    for address in addresses:
        file_path = create_envelope(address, return_address, output_dir, fonts)
        s3_link = upload_to_aws(file_path, bucket_name)
        if s3_link:
            s3_links.append(s3_link)
        os.remove(file_path)  # Clean up the local file after uploading
    return s3_links
