from datetime import datetime

def calculate_age(dob_str, today_date):
    """
    Calculates the age given the date of birth and the current date.

    Args:
    dob_str (str): Date of birth in 'YYYY-MM-DD' format.
    today_date (datetime.date): Today's date as a datetime.date object.

    Returns:
    int: Age in years.
    int: Age in days.
    """
    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    if isinstance(today_date, datetime):
        today_date = today_date.date()

    age_in_years = today_date.year - dob.year - ((today_date.month, today_date.day) < (dob.month, dob.day))
    age_in_days = (today_date - dob).days

    return age_in_years, age_in_days