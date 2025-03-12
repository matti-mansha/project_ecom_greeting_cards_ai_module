from flask import Blueprint, jsonify, request
from ai_module.utils._openai import message_generator
from ai_module.utils.utils_card import generate_card_png, generate_card_pdf
from ai_module.utils.envelope_util import create_envelopes_from_json, setup_fonts
from ai_module.utils.utils import load_config

from ai_module.utils.log_config import setup_logging
import logging
import json
import os

# Set up logging
setup_logging()

api_blueprint = Blueprint('api', __name__)

# Load configuration
config = load_config()
# generator = CardPDFGenerator(config)

# Setup fonts for the envelope
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to the ai_module directory
ai_module_dir = os.path.dirname(script_dir)

# Construct paths to font files
corinth_font_path = os.path.join(ai_module_dir, 'fonts', 'Corinth Two W01 Regular.ttf')
hello_mommy_font_path = os.path.join(ai_module_dir, 'fonts', 'HelloMommy.ttf')
aldo_font_path = os.path.join(ai_module_dir, 'fonts', 'Aldo.ttf')

try:
    setup_fonts(corinth_font_path, hello_mommy_font_path, aldo_font_path)
except Exception as e:
    logging.error(f"Error setting up fonts: {e}")

@api_blueprint.route('/hello')
def hello():
    return jsonify({'message': 'Hello from the API!'})

@api_blueprint.route('/generate_message', methods=['POST'])
def generate_message():
    try:
        data = request.json
        name = data.get('name')
        relationship = data.get('relationship')
        occasion = data.get('occasion')
        birthday = data.get('birthday')
        gender = data.get('gender')
        character_traits = data.get('character_traits')
        message_theme = data.get('message_theme')

        # Unpack the returned tuple from message_generator into four variables
        normal_1_paragraph, normal_2_paragraphs, short_and_sweet, poem = message_generator(
            name, relationship, occasion, birthday, gender, character_traits, message_theme
        )

        # Construct and return the JSON response
        return jsonify({
            "Normal1Paragraph": normal_1_paragraph,
            "Normal2Paragraphs": normal_2_paragraphs,
            "ShortAndSweet": short_and_sweet,
            "Poem": poem
        }), 200

    except Exception as e:
        logging.error(f"Error in generate_message: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    

# @api_blueprint.route('/generate_card_old', methods=['POST'])
# def generate_card():
#     try:
#         data = request.json
#         greeting = data.get('greeting')
#         body = data.get('body')
#         signoff = data.get('signoff')
#         thumbnail_path = data.get('thumbnail')  # Ensure this path is accessible on the server
#         last_page = "last-page.png"

#         # Synchronously generate the card PDF and upload it
#         s3_link = generate_card_pdf(greeting, body, signoff, thumbnail_path, last_page)

#         if s3_link:
#             return jsonify({'url': s3_link}), 200
#         else:
#             return jsonify({'error': 'Failed to generate or upload PDF'}), 500

#     except Exception as e:
#         logging.error(f"Error in generate_card: {e}", exc_info=True)
#         return jsonify({'error': str(e)}), 400
    
@api_blueprint.route('/generate_card', methods=['POST'])
def generate_card_pdf_():
    try:
        # Validate incoming JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        greeting = data.get('greeting')
        body = data.get('body')
        signoff = data.get('signoff')
        thumbnail = data.get('thumbnail')  # Ensure this path is accessible on the server

        if not all([greeting, body, signoff, thumbnail]):
                return jsonify({'error': 'Missing required fields: greeting, body, signoff, or thumbnail'}), 400
        
        last_page = "last-page.png"

        # Synchronously generate the card PDF and upload it
        s3_link = generate_card_pdf(greeting, body, signoff, thumbnail, last_page)

        if s3_link:
            return jsonify({'url': s3_link}), 200
        else:
            return jsonify({'error': 'Failed to generate or upload PDF'}), 500

    except Exception as e:
        logging.error(f"Error in generate_card: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
    

@api_blueprint.route('/generate_card_png', methods=['POST'])
def generate_card_png_():
    try:
        data = request.json
        greeting = data.get('greeting')
        body = data.get('body')
        signoff = data.get('signoff')

        # Call your existing function with the provided data
        # s3_link = generate_card_png(greeting=greeting, body=body, signoff=signoff, final_filename="generated.png")


        # Synchronously generate the card PDF and upload it
        s3_link = generate_card_png(greeting, body, signoff)

        # Check if an S3 link was successfully returned
        if s3_link:
            return jsonify({'page2': "https://tobre-cards.s3.us-east-2.amazonaws.com/images/13ecfe12-f78f-4653-a507-4574e34e8216-page02.png", 'page3': s3_link[0], 'last': s3_link[1]}), 200
        else:
            return jsonify({'error': 'Failed to generate or upload PDF'}), 500

    except Exception as e:
        logging.error(f"Error in generate_card_png: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400


@api_blueprint.route('/generate_envelope', methods=['POST'])
def generate_envelope():
    try:
        data = request.json
        return_address = data.get('return_address')
        addresses = data.get('addresses')
        
        bucket_name = config['AWS']['bucket_name']

        fonts = {
            'return': {'font': 'Aldo', 'size': 12},
            'return_address': {'font': 'Aldo', 'size': 12},
            'recipient': {'font': 'Aldo', 'size': 36},
            'recipient_address': {'font': 'Aldo', 'size': 18}
        }

        output_dir = 'envelopes'
        json_data = json.dumps(addresses)
        s3_links = create_envelopes_from_json(json_data, return_address, output_dir, fonts)

        return jsonify({'s3_links': s3_links}), 200

    except Exception as e:
        logging.error(f"Error in generate_envelope: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400
