import markdown2
from django.utils.safestring import mark_safe
from django import template
from django.urls import reverse

from app_dashboard.models import Thumbnail

register = template.Library()

@register.filter(name='remove_income_expense_words')
def remove_income_expense_words(text):
    return text.replace('INCOME - ', '').replace('EXPENSE - ', '')

@register.filter(name='format_vnd')
def format_vnd(amount):
    if amount is None:
        return ""
    # Convert the number to a string and reverse it
    try:
        amount_str = str(int(amount))[::-1]
    except Exception as e:
        return e

    # Insert a dot every 3 digits
    formatted_str = '.'.join(amount_str[i:i+3] for i in range(0, len(amount_str), 3))
    # Reverse the string back and append the VND symbol
    return formatted_str[::-1].replace('-.','-') + " VNĐ"


@register.filter
def calculate_bonus(balance_increase, amount):
    try:
        number = round((int(balance_increase) - int(amount)) / int(balance_increase)*100,1)
        result = str(number) + "%" 
        return result
    except ZeroDivisionError as e:
        return "0%"


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

@register.simple_tag
def get_thumbnail(image_url):
    if Thumbnail.objects.filter(reference_url=image_url).exists():
        try:
            thumbnail_url = Thumbnail.objects.filter(reference_url=image_url).first().thumbnail.url
        except Exception as e:
            thumbnail_url = str(e)
       
    else:
        thumbnail_url = 'no_thumbnail_found'
     
    return thumbnail_url


@register.filter(name="markdown")
def markdown_filter(text):
    if not text:
        return ""
    return mark_safe(
        markdown2.markdown(
            text, extras=["fenced-code-blocks", "tables", "break-on-newline"]
        )
    )