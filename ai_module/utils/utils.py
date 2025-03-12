from datetime import datetime
from openai import OpenAI
import configparser
import random
import json
import os
from openai import OpenAI
import logging
import os
import re


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



def extract_messages(greeting_card_message):
    """
    Extracts messages from a JSON-formatted greeting card message.
    
    This function is robust against inputs that may contain markdown code block
    delimiters or other irrelevant characters at the beginning or end of the JSON string.
    If JSON parsing fails, it attempts to extract messages using regular expressions.
    
    Args:
        greeting_card_message (str): JSON string containing greeting card messages.
    
    Returns:
        tuple: A tuple containing four message strings:
            - f_Normal1Paragraph
            - f_Normal2Paragraphs
            - f_ShortAndSweet
            - f_poem
    """
    # Initialize default messages
    f_Normal1Paragraph = ""
    f_Normal2Paragraphs = ""
    f_ShortAndSweet = ""
    f_poem = ""

    # Preprocess the input to remove code block markers and irrelevant characters
    def clean_json_input(s):
        """
        Cleans the input string by removing markdown code block delimiters
        and any leading/trailing irrelevant characters.

        Args:
            s (str): The raw input string.

        Returns:
            str: Cleaned JSON string.
        """
        s = s.strip()
        
        # Regex pattern to match code blocks with optional language specifier
        code_block_pattern = re.compile(r'^```(?:\w+)?\n?(.*?)```$', re.DOTALL)
        match = code_block_pattern.match(s)
        if match:
            return match.group(1).strip()
        return s

    cleaned_message = clean_json_input(greeting_card_message)

    # Attempt to parse JSON
    try:
        parsed_json = json.loads(cleaned_message)
        logging.info("JSON parsing succeeded.")
        # Proceed to extract messages as before
        f_Normal1Paragraph, f_Normal2Paragraphs, f_ShortAndSweet, f_poem = extract_from_json(parsed_json)
    except json.JSONDecodeError:
        logging.warning("JSON parsing failed. Attempting regex extraction.")
        # Fallback to regex extraction
        f_Normal1Paragraph, f_Normal2Paragraphs, f_ShortAndSweet, f_poem = extract_from_regex(cleaned_message)
    
    return f_Normal1Paragraph, f_Normal2Paragraphs, f_ShortAndSweet, f_poem


def extract_from_json(parsed_json):
    """
    Extracts messages from a parsed JSON object.

    Args:
        parsed_json (dict): Parsed JSON data.

    Returns:
        tuple: Extracted message strings.
    """
    f_Normal1Paragraph = ""
    f_Normal2Paragraphs = ""
    f_ShortAndSweet = ""
    f_poem = ""

    # Extract Normal1Paragraph
    normal1Paragraph = parsed_json.get("Normal1Paragraph", {})
    if isinstance(normal1Paragraph, dict):
        f_Normal1Paragraph = normal1Paragraph.get('Message', "")
        if not f_Normal1Paragraph:
            logging.warning("'Normal1Paragraph' message is missing.")
    else:
        logging.warning("'Normal1Paragraph' should be a dictionary.")

    # Extract Normal2Paragraphs
    normal2Paragraphs = parsed_json.get("Normal2Paragraphs", {})
    if isinstance(normal2Paragraphs, dict):
        para1 = normal2Paragraphs.get('para1', "")
        para2 = normal2Paragraphs.get('para2', "")
        if para1 or para2:
            f_Normal2Paragraphs = f"{para1}\n\n{para2}".strip()
        else:
            logging.warning("'Normal2Paragraphs' messages are missing.")
    else:
        logging.warning("'Normal2Paragraphs' should be a dictionary.")

    # Extract ShortAndSweet
    shortAndSweet = parsed_json.get("ShortAndSweet", {})
    if isinstance(shortAndSweet, dict):
        f_ShortAndSweet = shortAndSweet.get('Message', "")
        if not f_ShortAndSweet:
            logging.warning("'ShortAndSweet' message is missing.")
    else:
        logging.warning("'ShortAndSweet' should be a dictionary.")

    # Extract Poem
    poem = parsed_json.get("Poem", {})
    if isinstance(poem, dict):
        poem_lines = []
        # Assuming lines from line1 to line12
        for i in range(1, 13):
            line_key = f'line{i}'
            line = poem.get(line_key, "").rstrip('.,')
            if line:
                poem_lines.append(line)
                # Insert a blank line after the 4th line if more lines exist
                if i == 4 and any(poem.get(f'line{j}', "") for j in range(5, 13)):
                    poem_lines.append("")
        if poem_lines:
            f_poem = '\n'.join(poem_lines)
        else:
            logging.warning("'Poem' lines are missing.")
    else:
        logging.warning("'Poem' should be a dictionary.")

    return f_Normal1Paragraph, f_Normal2Paragraphs, f_ShortAndSweet, f_poem


def extract_from_regex(text):
    """
    Extracts messages using regular expressions from a text string.

    Args:
        text (str): The input text containing messages.

    Returns:
        tuple: Extracted message strings.
    """
    f_Normal1Paragraph = ""
    f_Normal2Paragraphs = ""
    f_ShortAndSweet = ""
    f_poem = ""

    # Define regex patterns for each message category
    patterns = {
        "Normal1Paragraph": r'"Normal1Paragraph"\s*:\s*\{[^}]*"Message"\s*:\s*"([^"]+)"',
        "Normal2Paragraphs_para1": r'"Normal2Paragraphs"\s*:\s*\{[^}]*"para1"\s*:\s*"([^"]+)"',
        "Normal2Paragraphs_para2": r'"Normal2Paragraphs"\s*:\s*\{[^}]*"para2"\s*:\s*"([^"]+)"',
        "ShortAndSweet": r'"ShortAndSweet"\s*:\s*\{[^}]*"Message"\s*:\s*"([^"]+)"',
        # For Poem, capture all lines
        "Poem": r'"Poem"\s*:\s*\{([^}]+)\}'
    }

    # Extract Normal1Paragraph
    match = re.search(patterns["Normal1Paragraph"], text, re.DOTALL)
    if match:
        f_Normal1Paragraph = match.group(1).strip()
    else:
        logging.warning("Regex extraction failed for 'Normal1Paragraph'.")

    # Extract Normal2Paragraphs
    para1 = re.search(patterns["Normal2Paragraphs_para1"], text, re.DOTALL)
    para2 = re.search(patterns["Normal2Paragraphs_para2"], text, re.DOTALL)
    if para1 and para2:
        f_Normal2Paragraphs = f"{para1.group(1).strip()}\n\n{para2.group(1).strip()}"
    else:
        logging.warning("Regex extraction failed for 'Normal2Paragraphs'.")

    # Extract ShortAndSweet
    match = re.search(patterns["ShortAndSweet"], text, re.DOTALL)
    if match:
        f_ShortAndSweet = match.group(1).strip()
    else:
        logging.warning("Regex extraction failed for 'ShortAndSweet'.")

    # Extract Poem
    poem_match = re.search(patterns["Poem"], text, re.DOTALL)
    if poem_match:
        poem_content = poem_match.group(1)
        # Extract all lines within Poem
        lines = re.findall(r'"line\d+"\s*:\s*"([^"]+)"', poem_content)
        poem_lines = [line.rstrip('.,') for line in lines if line]
        # Insert a blank line after the 4th line if more lines exist
        if len(poem_lines) > 4:
            poem_lines.insert(4, "")
        if poem_lines:
            f_poem = '\n'.join(poem_lines)
    else:
        logging.warning("Regex extraction failed for 'Poem'.")

    return f_Normal1Paragraph, f_Normal2Paragraphs, f_ShortAndSweet, f_poem


def select_random_traits(important_traits, character_traits, number=4):
    # Check if the list is empty or not provided
    if not important_traits or not character_traits:
        return ["Just focus on the occasion."]
    
    # Filter traits that are relevant to the occasion
    relevant_traits = [trait for trait in character_traits if trait in important_traits]
    
    # For a 50/50 split, simply balance the number of important trait entries with occasion focus entries
    if relevant_traits:
        # Determine the number of entries for each type based on the total number requested
        num_important_traits = number // 2
        num_occasion_focus = number - num_important_traits  # Ensure the total is always as requested
        
        # If there are fewer relevant traits than the slots allocated, adjust the numbers
        if len(relevant_traits) < num_important_traits:
            num_important_traits = len(relevant_traits)
            num_occasion_focus = number - num_important_traits
        
        weighted_important_traits = random.sample(relevant_traits, num_important_traits)
        occasion_focus_entries = ["Just focus on the spirit of the occasion."] * num_occasion_focus
        
        # Combine and shuffle to avoid predictable ordering
        weighted_traits = weighted_important_traits + occasion_focus_entries
        random.shuffle(weighted_traits)
    else:
        # If no relevant traits, fill with occasion focus
        weighted_traits = ["Just focus on the spirit of the occasion."] * number
    
    # Select the traits or phrases based on the weighted list without needing further sampling
    selected = weighted_traits[:number]
    
    # Ensure at least one selection is focused on the spirit of the occasion if all traits were chosen
    if all(trait in important_traits for trait in selected):
        if len(selected) > 1 and "Just focus on the spirit of the occasion." not in important_traits:
            selected[-1] = "Just focus on the spirit of the occasion."
        elif len(selected) == 1:
            selected.append("Just focus on the spirit of the occasion.")
    
    return selected


def select_random_themes(themes, number=4):
    """
    Selects a specified number of themes randomly from a list of themes. Themes can be repeated if the list is shorter than the required number.
    :param themes: A list of themes.
    :param number: The number of themes to select.
    :return: A list of themes selected randomly, with possible repetitions.
    """
    return [random.choice(themes) for _ in range(number)] if themes else None


def gpt_core_of_occasion(occasion):
    logging.info("Generating GPT response of core of occasion...")
    logging.info(f"Occasion: {occasion}")

    # Create OpenAI client
    logging.info("Creating OpenAI client...")
    # client = OpenAI()
    client = OpenAI(
        api_key=config['OPENAI']['GOOGLE_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    prompt = """
    If I were an alien and I didn't know anything about {occasion}, in 4 bullet points explain to be me what
    the main spirit of the holiday is about
    """

    prompt = prompt.format(
        occasion=occasion
    )

    logging.info("Prompt:")
    logging.info(prompt)
    
    logging.info("Calling OpenAI API...")
    completion = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a curious alien who wants to learn about the holiday."},
        {"role": "user", "content": prompt}
    ]
    )

    return completion.choices[0].message.content


def get_core_of_the_event(occasion):
    occasion_descriptions = {
        "Christmas": """
        Christmas is a celebration that commemorates the birth of Jesus Christ, highlighting joy and significance in Christianity. It involves the tradition of exchanging gifts to symbolize love, generosity, and goodwill. The holiday also emphasizes family togetherness, encouraging quality time, shared meals, and memory-making among loved ones. Characterized by a festive atmosphere, Christmas features decorations, lights, and music, fostering a sense of merriment and engaging people in activities to spread cheer.
        """,

        "Easter": """
        Easter celebrates the resurrection of Jesus Christ, symbolizing hope, renewal, and the victory of good over evil, while prompting reflection on spiritual matters. The holiday is marked by fertility symbols like eggs and bunnies, representing life's cycle and new beginnings. Similar to Christmas, it's a time for family gatherings, special meals, and appreciating familial bonds. Easter also includes religious observances, with many attending church services to honor the resurrection's significance in Christian faith.
        """,

        "Mother's Day": """
        Mother's Day is dedicated to honoring mothers and maternal figures, acknowledging their love, sacrifices, and contributions to family life. It's a day marked by gift-giving, cards, and gestures of affection, aiming to make mothers feel appreciated and cherished. Spending quality time together, through meals, outings, or simply enjoying each other's company, is essential, focusing on creating meaningful experiences. The day serves as an opportunity to express gratitude and love, thanking mothers for their pivotal role in shaping lives.
        """,

        "Father's Day": """
        Father's Day is dedicated to celebrating fathers and paternal figures, recognizing their contributions to families and society. It mirrors Mother's Day in expressing gratitude, love, and appreciation with gifts, cards, and thoughtful gestures. The day encourages engaging in activities fathers enjoy, like outdoor adventures, hobbies, or special meals, aiming to make them feel valued. It highlights the significance of quality time and bonding, strengthening family connections.
        """,

        "Valentines": """
        Valentine's Day is dedicated to expressing love and affection, celebrating not just romantic love but also the love for friends and family. It's marked by romantic gestures, with couples exchanging cards, flowers, and gifts, and enjoying romantic dinners or special outings. The day encourages acts of kindness, prompting people to show appreciation and affection for their loved ones. Serving as a thoughtful reminder, Valentine's Day underscores the importance of cherishing relationships that bring joy and fulfillment, offering a chance to openly express feelings and strengthen emotional connections.
        """,
        
        "New Year's": """
        New Year's symbolizes a fresh start and the opportunity for renewal, both personally and collectively, marked by goal setting and resolutions. New Year's Eve is celebrated with parties, fireworks, and festivities, emphasizing joyous gatherings and the countdown to a new beginning. It's a time for reflection on the past year, acknowledging achievements, learning from challenges, and expressing gratitude. The transition embodies hope and anticipation for the future, looking forward to the possibilities and opportunities the new year may present.
        """,

        "Thanks Giving": """
        Thanksgiving revolves around expressing gratitude and reflecting on life's blessings and abundance. It fosters appreciation for positive aspects and relationships. The holiday is characterized by special meals, often featuring turkey, shared among family and friends, symbolizing unity and the significance of communal bonds. Acts of kindness, such as volunteering or supporting charities, are common, highlighting the spirit of giving back and expressing thankfulness. Emphasizing family bonding, Thanksgiving is a time for reinforcing familial ties and creating lasting memories through shared experiences.
        """,

        "Anniversary": """
        A wedding anniversary celebrates a couple's union in marriage, marking their commitment, love, and partnership. It's an occasion for reflection on the couple's shared journey, including significant moments, challenges overcome, and the growth of their relationship. The celebration often features romantic gestures like exchanging gifts, special outings, or writing heartfelt messages to express love and appreciation. Additionally, some couples opt to renew their vows, reaffirming their commitment in a meaningful ceremony.
        """,

        "Birthday": """
        A birthday is a celebration of a person's birth, marking the passage of another year of life. It's an occasion for reflection on the individual's growth, achievements, and the love and support they have received from family and friends. The celebration often includes special meals, gifts, and activities that make the individual feel valued and celebrated. It's a time to look back on the past year and look forward to the year ahead, with gratitude for the blessings and opportunities that have come their way.
        """
    }
    
    # Check if the occasion is in the dictionary; if not, call a generic function
    return occasion_descriptions.get(occasion, gpt_core_of_occasion(occasion))


def get_important_traits(occasion):
    if occasion == "Christmas":
        return ["Kind", "Loving", "Generous", "Compassionate"]
    elif occasion == "Easter":
        return ["Kind", "Loving", "Generous", "Compassionate"]
    elif occasion == "Mother's Day":
        return ["Kind", "Loving", "Generous", "Compassionate", "Wise"]
    elif occasion == "Father's Day":
        return ["Kind", "Loving", "Generous", "Compassionate", "Wise"]
    elif occasion == "New Year's":
        return ["Adventurous", "Loving", "Generous", "Creative"]
    elif occasion == "Valentines":
        return ["Kind", "Loving", "Compassionate", "Patient", "Gentle"]
    elif occasion == "Thanks Giving":
        return ["Kind", "Loving", "Generous", "Compassionate"]
    elif occasion == "Anniversary":
        return ["Kind", "Loving", "Generous", "Compassionate", "Gentle", "Patient", "Adventurous"]
    else:
        return ["Kind", "Loving", "Wise", "Honest", "Generous", "Humorous", "Compassionate", "Patient", "Adventurous", "Gentle", "Loyal", "Caring", "Creative"]