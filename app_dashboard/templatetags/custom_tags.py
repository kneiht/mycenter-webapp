from django import template

register = template.Library()


@register.inclusion_tag('components/display_cards.html')
def display_cards(page, records):
    if page=='schools':
        context = {'select': 'schools', 'records': records}
    elif page=='classes':
        context = {'select': 'classes', 'records': records}
    elif page=='students':
        context = {'select': 'students', 'records': records}
    elif page=='dashboard':
        context = {'select': 'dashboard'}
    return context



@register.simple_tag
def my_simple_tag(arg1, arg2):
    # Your processing here
    return "something"


@register.filter
def my_filter(value, arg):
    # Your processing here
    return "processed value"
