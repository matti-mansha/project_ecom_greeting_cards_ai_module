from datetime import datetime
from openai import OpenAI
import logging
import os
import random

from ai_module.utils.helpers import calculate_age
from ai_module.utils.utils import load_config, extract_messages, select_random_themes,\
select_random_traits, get_core_of_the_event, get_important_traits

# Load configuration
config = load_config()

os.environ['OPENAI_API_KEY'] = config['OPENAI']['OPENAI_API_KEY']
api = config['OPENAI']['GOOGLE_API_KEY']


def gpt_res(name, relationship, occasion, birthday, gender, random_traits, random_message_themes):
    logging.info("Generating GPT response...")
    logging.info(f"Name: {name}")
    logging.info(f"Relationship: {relationship}")
    logging.info(f"Occasion: {occasion}")
    logging.info(f"Birthday: {birthday}")
    logging.info(f"Gender: {gender}")
    logging.info(f"Traits: {random_traits}")
    logging.info(f"Themes: {random_message_themes}")
    logging.info(f"Core of the event: {get_core_of_the_event(occasion)}")


    # Calculate age
    today_date = datetime.now().date()
    age_years, _ = calculate_age(birthday, today_date)
    logging.info(f"Age: {age_years}")

    # Create OpenAI client
    logging.info("Creating OpenAI client...")
    # client = OpenAI()
    client = OpenAI(
        api_key=api,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    prompt1 = """
    Create four styles of greeting card messages for a {relationship} on the occasion of {occasion}, considering their personality trait, our relationship, and the spirit of the event as described:
    
    Spirit of the Event: {spirit_of_event}
    
    - Message 1: Normal, 1 paragraph, themed "{message_theme_1}", including trait "{trait_1}" and capturing the spirit of {occasion}.
    - Message 2: Normal, 2 paragraphs, themed "{message_theme_2}", including trait "{trait_2}". Each paragraph should not exceed 20 words and should capture the essence of {occasion}.
    - Message 3: Short and sweet, themed "{message_theme_3}", with trait "{trait_3}" and reflecting the spirit of {occasion}.
    - Message 4: Poem style, themed "{message_theme_4}", reflecting trait "{trait_4}" and the spirit of {occasion}. Comprise 4 lines. Max 12 words per stanza


    Each message should be 5-40 words long, no shorter than one sentence and no longer than three sentences. Include new lines between lines, paragraphs, and stanzas. 
    
    The messages are tailored for events around Christmas, New Year's, Easter, and Thanksgiving to capture more of the spirit of the event versus concentrating on the person alone.
    
    Don't Forget:
    Each message should be clear, impactful, and appropriately themed. The messages are tailored for {occasion} to capture the spirit of the event.


    Details:
    Gender: {gender}
    {relationship}'s Age: {age_years}
    

    Output Format (in JSON):
    {{
        "Normal1Paragraph": {{"Trait": "{trait_1}", "Theme": "{message_theme_1}", "Message": "<Message>"}},
        "Normal2Paragraphs": {{"Trait": "{trait_2}", "Theme": "{message_theme_2}", "para1": "<paragraph 1>", "para2": "<paragraph 2>"}},
        "ShortAndSweet": {{"Trait": "{trait_3}", "Theme": "{message_theme_3}", "Message": "<Message>"}},
        "Poem": {{"Trait": "{trait_4}", "Theme": "{message_theme_4}", "line1": "<Opening line>", "line2": "<line 2>", "line3": "<line 3>", "line4": "<Closing line>"}}
    }}
    """

    prompt2 = """
    Create four styles of greeting card messages for a {relationship} on the occasion of {occasion}, considering their personality trait, our relationship, and the spirit of the event as described:
    
    Spirit of the Event: {spirit_of_event}
    
    - Message 1: Normal, 1 paragraph, themed "{message_theme_1}", including trait "{trait_1}" and capturing the spirit of {occasion}.
    - Message 2: Normal, 2 paragraphs, themed "{message_theme_2}", including trait "{trait_2}". Each paragraph should not exceed 20 words and should capture the essence of {occasion}.
    - Message 3: Short and sweet, themed "{message_theme_3}", with trait "{trait_3}" and reflecting the spirit of {occasion}.
    - Message 4: Poem style, themed "{message_theme_4}", reflecting trait "{trait_4}" and the spirit of {occasion}. Comprise 8 lines. Max 12 words per stanza


    Each message should be 5-40 words long, no shorter than one sentence and no longer than three sentences. Include new lines between lines, paragraphs, and stanzas. 
    
    The messages are tailored for events around Christmas, New Year's, Easter, and Thanksgiving to capture more of the spirit of the event versus concentrating on the person alone.
    
    Don't Forget:
    Each message should be clear, impactful, and appropriately themed. The messages are tailored for {occasion} to capture the spirit of the event.


    Details:
    Gender: {gender}
    {relationship}'s Age: {age_years}
    

    Output Format (in JSON):
    {{
        "Normal1Paragraph": {{"Trait": "{trait_1}", "Theme": "{message_theme_1}", "Message": "<Message>"}},
        "Normal2Paragraphs": {{"Trait": "{trait_2}", "Theme": "{message_theme_2}", "para1": "<paragraph 1>", "para2": "<paragraph 2>"}},
        "ShortAndSweet": {{"Trait": "{trait_3}", "Theme": "{message_theme_3}", "Message": "<Message>"}},
        "Poem": {{"Trait": "{trait_4}", "Theme": "{message_theme_4}", "line1": "<Opening line>", "line2": "<line 2>", "line3": "<line 3>", "line4": "<line 4>", "line5": "<line 5>", "line6": "<line 6>", "line7": "<line 7>", "line8": "<Closing line>"}}
    }}
    """

    prompts = [prompt1, prompt2]

    # Select a random prompt
    prompt = random.choice(prompts)

    prompt = prompt.format(
        message_theme_1=random_message_themes[0],
        trait_1=random_traits[0],
        message_theme_2=random_message_themes[1],
        trait_2=random_traits[1],
        message_theme_3=random_message_themes[2],
        trait_3=random_traits[2],
        message_theme_4=random_message_themes[3],
        trait_4=random_traits[3],
        occasion=occasion,
        relationship=relationship,
        today_date=today_date,
        dob = birthday,
        name = name,
        gender = gender,
        age_years = age_years,
        spirit_of_event = get_core_of_the_event(occasion)
    )

    logging.info("Prompt:")
    logging.info(prompt)
    
    logging.info("Calling OpenAI API...")
    completion = client.chat.completions.create(
    # model="gpt-3.5-turbo",
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a pro Geeting card text generator."},
        {"role": "user", "content": prompt}
    ]
    )
    
    logging.info("Full Response:")
    logging.info(completion)

    return completion.choices[0].message.content


# name = "Zahra"
# relationship = "Sister"
# occasion = "birthday"
# birthday = "2000-11-26"  # YYYY-MM-DD format
# gender = "female"
# random_traits = ["kind", "funny", "thoughtful", "creative"]
# random_message_themes = ["heartwarming", "humorous", "inspirational", "poetic"]

# # Call the function with the sample inputs
# greeting_message = gpt_res(name, relationship, occasion, birthday, gender, random_traits, random_message_themes)

# print(greeting_message)
# print("====================================")
# print(extract_messages(greeting_message))


def message_generator(name, relationship, occasion, birthday, gender, character_traits, message_theme):
    """
    Generates a greeting card message based on given parameters.

    Args:
    name (str): Name of the person.
    relationship (str): The relationship with the person.
    occasion (str): The occasion for the message.
    birthday (str): The birthday of the person.
    gender (str): The gender of the person.
    character_traits (list): A list of character traits.
    message_theme (list): A list of message themes.

    Returns:
    tuple: A tuple containing generated messages or an error message.
    """
    # Validate inputs
    if not (isinstance(character_traits, list) and len(character_traits) >= 3):
        raise ValueError("character_traits must be a list of at least 3 items.")
    if not (isinstance(message_theme, list) and len(message_theme) >= 1):
        raise ValueError("message_theme must be a list of at least 1 items.")
    
    if not all(isinstance(x, str) and x for x in [name, relationship, occasion, gender]):
        raise ValueError("name, relationship, occasion, and gender must be non-empty strings.")

    # Validate birthday format
    try:
        datetime.strptime(birthday, '%Y-%m-%d')
    except ValueError:
        raise ValueError("birthday must be a string in 'YYYY-MM-DD' format.")

    try:
        logging.info("Generating greeting card message...")


        important_traits = get_important_traits(occasion)
        logging.info(f"Important traits: {important_traits}")

        selected_imp_traits = [trait for trait in character_traits if trait in important_traits]
        logging.info(f"Selected important traits: {selected_imp_traits}")

        selected_non_imp_traits = [trait for trait in character_traits if trait not in important_traits]
        logging.info(f"Selected non-important traits: {selected_non_imp_traits}")


        # random_trait = select_random_traits(character_traits)
        random_trait = select_random_traits(selected_imp_traits, character_traits)
        logging.info(f"Randomly selected traits: {random_trait}")

        random_theme = select_random_themes(message_theme)
        logging.info(f"Randomly selected themes: {random_theme}")   

        response = gpt_res(name, relationship, occasion, birthday, gender, random_trait, random_theme)
        logging.info(f"Response: {response}")

        try:
            logging.info("Extracting messages...")
            extracted_messages = extract_messages(response)
            logging.info(f"Extracted messages: {extracted_messages}")
            return extracted_messages[0], extracted_messages[1], extracted_messages[2], extracted_messages[3]
        except Exception as extract_error:
            logging.error(f"Error extracting messages: {extract_error}")
            logging.info("Retrying...")
            # Handle error in extract_messages and retry gpt_res call
            response = gpt_res(name, relationship, occasion, birthday, gender, random_trait, random_theme)
            extracted_messages = extract_messages(response)
            return extracted_messages[0], extracted_messages[1], extracted_messages[2], extracted_messages[3]
        
    except Exception as e:
        logging.error(f"An error occurred during message generation: {e}", exc_info=True)
        return f"An error occurred: {e}"