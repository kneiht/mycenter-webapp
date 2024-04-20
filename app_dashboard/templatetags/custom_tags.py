
from django import template
from django.urls import reverse



register = template.Library()

@register.filter(name='format_vnd')
def format_vnd(amount):
    # Convert the number to a string and reverse it
    amount_str = str(int(amount))[::-1]
    
    # Insert a dot every 3 digits
    formatted_str = '.'.join(amount_str[i:i+3] for i in range(0, len(amount_str), 3))
    # Reverse the string back and append the VND symbol
    return formatted_str[::-1].replace('-.','-') + " VNĐ"


@register.filter
def calculate_bonus(value, arg):
    try:
        number = round(int(value) / int(arg), 3) - 1
        result = "Extra " + str(number*100) + "%" 
        return result
    except (ValueError, ZeroDivisionError):
        return


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

