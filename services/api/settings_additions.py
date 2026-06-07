
# ============================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# Add these to your settings.py
# ============================================================

INSTALLED_APPS = [
    # ... your existing apps ...
    'rest_framework',
    'rest_framework.authtoken',  # Optional: if you want token auth too
    'corsheaders',  # For mobile app CORS
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'services.authentication.APIKeyAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # For web browsable API
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'services.pagination.StandardPagination',
    'DEFAULT_THROTTLE_CLASSES': [
        'services.throttling.AnonBurstRateThrottle',
        'services.throttling.AnonSustainedRateThrottle',
        'services.throttling.UserBurstRateThrottle',
        'services.throttling.UserSustainedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon_burst': '5/minute',
        'anon_sustained': '100/day',
        'user_burst': '60/minute',
        'user_sustained': '1000/day',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'services.utils.custom_exception_handler',
}

# CORS settings for mobile app
CORS_ALLOWED_ORIGINS = [
    # Add your mobile app domain if needed
    # 'https://yourapp.com',
]

CORS_ALLOW_ALL_ORIGINS = True  # Set to False in production

# API Key header name
API_KEY_HEADER = 'X-API-Key'
