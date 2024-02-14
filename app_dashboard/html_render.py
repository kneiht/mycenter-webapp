from django.template.loader import render_to_string

def html_render( component, request, **kwargs):
    if component=='card':
        context = {
                'select': kwargs.get('select'),
                'record': kwargs.get('record'), 
                'card': kwargs.get('card'),
                'base_url': kwargs.get('base_url'),
                'school': kwargs.get('school'),
        }
        template = 'components/card.html'

    elif component=='message':
        context = {
                'modal': 'modal_message', 
                'message': kwargs.get('message'),
        }
        template = 'components/modal.html'

    elif component=='form':
        context = {
                'form': kwargs.get('form'), 
                'modal': kwargs.get('modal'),
                'record_id': kwargs.get('record_id'),
                'base_url': kwargs.get('base_url'),
                'school_id': kwargs.get('school_id'),
        }
        template = 'components/modal.html'
    
    elif component=='display_cards':
        context = {
                'select': kwargs.get('select'),
                'records': kwargs.get('records'), 
                'card': kwargs.get('card'),
                'base_url': kwargs.get('base_url'),
                'school': kwargs.get('school'),
        }
        template = 'components/display_cards.html'

    return render_to_string(template, context, request)