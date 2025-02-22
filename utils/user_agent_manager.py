from fake_useragent import UserAgent


# Initialize the UserAgent instance
def get_random_user_agent():
    """
    Generate a random User-Agent string.

    This function uses the `fake_useragent` library to return a random
    User-Agent string from a variety of browsers and platforms.

    Returns:
        str: A randomly selected User-Agent string.
    """
    ua = UserAgent()
    return ua.random
