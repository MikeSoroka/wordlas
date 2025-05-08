from project.settings import *

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Skip the API migrations for testing the main app's models
MIGRATION_MODULES = {
    'api': None,  # Skip API migrations
}
