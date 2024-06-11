
from django import template
from django.urls import reverse



register = template.Library()

@register.filter(name='format_vnd')
def format_vnd(amount):
    if amount is None:
        return 'errorNontype'
    # Convert the number to a string and reverse it
    amount_str = str(int(amount))[::-1]
    
    # Insert a dot every 3 digits
    formatted_str = '.'.join(amount_str[i:i+3] for i in range(0, len(amount_str), 3))
    # Reverse the string back and append the VND symbol
    return formatted_str[::-1].replace('-.','-') + " VNĐ"


@register.filter
def calculate_bonus(value, arg):
    try:
        number = round(int(value) / int(arg) - 1,3)
        result = "Extra " + str(number*100) + "%" 
        return result
    except Exception as e:
        return e


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



@register.filter
def multiply(value, arg):
    return value * arg



import qrcode
import qrcode.image.svg
from django.utils.safestring import mark_safe

@register.simple_tag
def qr_from_text(text):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(text, image_factory = factory)
    return mark_safe(img.to_string(encoding='unicode'))


@register.simple_tag
def convert_zalo_link(link):
    link = link.replace('https://','').replace('zalo.me/g/','')
    new_link = f'https://zaloapp.com/qr/g/{link}?src=qr'
    return new_link
