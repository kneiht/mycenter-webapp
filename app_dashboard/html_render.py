from django.template.loader import render_to_string

def html_render( component, request, **kwargs):
    if component=='card':
        context = {
                'record': kwargs.get('record'), 
                'card': kwargs.get('card'),
                'model_url': kwargs.get('model_url'),
                'swap_oob': 'hx-swap-oob="true"' if kwargs.get('swap_oob') else '',
        }
        template = 'components/card.html'

    elif component=='message':
        context = {
                'modal': 'modal_message', 
                'message': kwargs.get('message'),
                'swap_oob': 'hx-swap-oob="true"',
        }
        template = 'components/modal.html'

    elif component=='form':
        context = {
                'form': kwargs.get('form'), 
                'modal': kwargs.get('modal'),
                'record_id': kwargs.get('record_id'),
                'model_url': kwargs.get('model_url'),
                'swap_oob': 'hx-swap-oob="true"',
        }
        template = 'components/modal.html'
    
    elif component=='display_cards':
        context = {
                'records': kwargs.get('records'), 
                'card': kwargs.get('card'),
                'model_url': kwargs.get('model_url'),
                'swap_oob': 'hx-swap-oob="true"',
        }
        template = 'components/display_cards.html'

    elif component=='title_bar':
        context = {
                'page_title': kwargs.get('page_title'),
                'model_url': kwargs.get('model_url'),
                'swap_oob': 'hx-swap-oob="true"',
        }
        template = 'components/title_bar.html'

    elif component=='db_tool_bar':
        context = {
                'db_tool_bar': kwargs.get('for_manage_schools'),
                'model_url': kwargs.get('model_url'),
                'swap_oob': 'hx-swap-oob="true"',
        }
        template = 'components/db_tool_bar.html'

    return render_to_string(template, context, request)
