import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Set up basic configuration
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    # Create a file handler for output file
    file_handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)

    # Set the logging level and format for the file handler
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                '%Y-%m-%d %H:%M:%S'))

    # Add the file handler to the root logger
    logging.getLogger('').addHandler(file_handler)
