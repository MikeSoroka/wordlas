def theme_context(request):
    """
    Context processor to provide theme information to all templates.
    Gets theme preference from cookies or defaults to light theme.
    """
    theme = request.COOKIES.get('theme', 'light')
    return {
        'theme': theme
    } 