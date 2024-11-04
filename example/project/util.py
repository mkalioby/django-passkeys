def load_env(path):
    """
    Load variables from a file named .env
    Format:
    VARIABLE_NAME = value

    returns a dictionary with variables

    python-dotenv implements similar functionality.
    """

    # default data
    data = {
        'DJANGO_PASSKEY_HOST': 'localhost'
    }

    env_file = path / '.env'
    if not env_file.exists():
        print("Please create env file!")
        return data

    with open(env_file, 'r') as fh:
        for line in fh:
            try:
                key, value = line.split('=')
                key = key.strip().upper()
                value = value.strip()
                data[key] = value
            except:
                pass

    return data
