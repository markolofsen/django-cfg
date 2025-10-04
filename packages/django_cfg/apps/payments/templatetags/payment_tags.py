"""
Universal Payment System v2.0 - Template Tags

Custom Django template tags for payment system components.
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from decimal import Decimal
import json

register = template.Library()


@register.simple_tag
def material_icon(icon_name, variant='outlined', size='md', css_class=''):
    """
    Render a Material Icon with proper styling.
    
    Usage:
    {% material_icon 'payment' %}
    {% material_icon 'check_circle' variant='round' size='lg' css_class='text-green-600' %}
    """
    size_classes = {
        'xs': 'text-xs',
        'sm': 'text-sm', 
        'md': 'text-base',
        'lg': 'text-lg',
        'xl': 'text-xl',
        '2xl': 'text-2xl'
    }
    
    variant_class = f'material-icons-{variant}' if variant != 'filled' else 'material-icons'
    size_class = size_classes.get(size, 'text-base')
    
    classes = f'{variant_class} {size_class} {css_class}'.strip()
    
    return format_html(
        '<span class="{}">{}</span>',
        classes,
        icon_name
    )


@register.simple_tag
def status_badge(status, show_icon=True):
    """
    Render a status badge with appropriate styling and icon.
    
    Usage:
    {% status_badge payment.status %}
    {% status_badge 'completed' show_icon=False %}
    """
    status_config = {
        'completed': {
            'class': 'status-badge success',
            'icon': 'check_circle',
            'text': 'Completed'
        },
        'confirmed': {
            'class': 'status-badge success',
            'icon': 'verified',
            'text': 'Confirmed'
        },
        'pending': {
            'class': 'status-badge warning',
            'icon': 'schedule',
            'text': 'Pending'
        },
        'processing': {
            'class': 'status-badge info',
            'icon': 'sync',
            'text': 'Processing'
        },
        'failed': {
            'class': 'status-badge error',
            'icon': 'error',
            'text': 'Failed'
        },
        'cancelled': {
            'class': 'status-badge error',
            'icon': 'cancel',
            'text': 'Cancelled'
        },
        'active': {
            'class': 'status-badge success',
            'icon': 'check_circle',
            'text': 'Active'
        },
        'inactive': {
            'class': 'status-badge error',
            'icon': 'radio_button_unchecked',
            'text': 'Inactive'
        }
    }
    
    config = status_config.get(status.lower(), {
        'class': 'status-badge info',
        'icon': 'help',
        'text': status.title()
    })
    
    icon_html = ''
    if show_icon:
        icon_html = format_html(
            '<span class="material-icons-outlined mr-1" style="font-size: 14px;">{}</span>',
            config['icon']
        )
    
    return format_html(
        '<span class="{}">{}{}</span>',
        config['class'],
        icon_html,
        config['text']
    )


@register.simple_tag
def status_indicator(status):
    """
    Render a small status indicator dot.
    
    Usage:
    {% status_indicator payment.status %}
    """
    status_classes = {
        'completed': 'status-active',
        'confirmed': 'status-active', 
        'active': 'status-active',
        'pending': 'status-warning',
        'processing': 'status-warning',
        'failed': 'status-inactive',
        'cancelled': 'status-inactive',
        'inactive': 'status-inactive'
    }
    
    css_class = status_classes.get(status.lower(), 'status-warning')
    
    return format_html(
        '<span class="status-indicator {}"></span>',
        css_class
    )


@register.simple_tag
def format_currency(amount, currency='USD', show_symbol=True):
    """
    Format currency amount with proper locale formatting.
    
    Usage:
    {% format_currency payment.amount_usd %}
    {% format_currency payment.amount_crypto 'BTC' %}
    """
    try:
        amount = float(amount) if amount else 0
        
        if currency == 'USD' and show_symbol:
            return f'${amount:,.2f}'
        elif currency == 'USD':
            return f'{amount:,.2f}'
        else:
            # For crypto currencies, show more decimal places
            if amount >= 1:
                formatted = f'{amount:,.8f}'.rstrip('0').rstrip('.')
            else:
                formatted = f'{amount:.8f}'.rstrip('0').rstrip('.')
            
            return f'{formatted} {currency}' if show_symbol else formatted
            
    except (ValueError, TypeError):
        return f'0 {currency}' if show_symbol else '0'


@register.simple_tag
def payment_card(title, icon='payment', content='', css_class=''):
    """
    Render a payment card container.
    
    Usage:
    {% payment_card 'Payment Details' 'receipt_long' %}
    """
    return format_html(
        '''
        <div class="payment-card {}">
            <div class="payment-card-header">
                <h2 class="payment-card-title">
                    <span class="material-icons-outlined">{}</span>
                    {}
                </h2>
            </div>
            <div class="payment-card-content">
                {}
            </div>
        </div>
        ''',
        css_class,
        icon,
        title,
        content
    )


@register.simple_tag
def copy_button(text, tooltip='Copy to clipboard'):
    """
    Render a copy-to-clipboard button.
    
    Usage:
    {% copy_button payment.id %}
    {% copy_button webhook_url 'Copy webhook URL' %}
    """
    return format_html(
        '''
        <button onclick="PaymentSystem.Utils.copyToClipboard('{}')" 
                class="btn-icon text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                title="{}">
            <span class="material-icons-outlined text-sm">content_copy</span>
        </button>
        ''',
        text,
        tooltip
    )


@register.simple_tag
def loading_spinner(size='md', text=''):
    """
    Render a loading spinner.
    
    Usage:
    {% loading_spinner %}
    {% loading_spinner 'lg' 'Loading...' %}
    """
    spinner_html = format_html(
        '<div class="loading-spinner {}"></div>',
        size
    )
    
    if text:
        return format_html(
            '<div class="flex items-center space-x-2">{}<span>{}</span></div>',
            spinner_html,
            text
        )
    
    return spinner_html


@register.simple_tag
def action_button(text, icon, action='', css_class='btn-primary', disabled=False):
    """
    Render an action button with icon.
    
    Usage:
    {% action_button 'Create Payment' 'add' 'createPayment()' %}
    {% action_button 'Refresh' 'refresh' css_class='btn-secondary' %}
    """
    disabled_attr = 'disabled' if disabled else ''
    disabled_class = 'opacity-50 cursor-not-allowed' if disabled else ''
    
    onclick_attr = f'onclick="{action}"' if action else ''
    
    return format_html(
        '''
        <button {} {} class="{} {}">
            <span class="material-icons-outlined">{}</span>
            {}
        </button>
        ''',
        onclick_attr,
        disabled_attr,
        css_class,
        disabled_class,
        icon,
        text
    )


@register.filter
def json_encode(value):
    """
    JSON encode a value for use in JavaScript.
    
    Usage:
    {{ payment_data|json_encode }}
    """
    return mark_safe(json.dumps(value))


@register.filter
def truncate_id(value, length=8):
    """
    Truncate an ID for display.
    
    Usage:
    {{ payment.id|truncate_id }}
    {{ payment.id|truncate_id:12 }}
    """
    if not value:
        return ''
    
    str_value = str(value)
    if len(str_value) <= length:
        return str_value
    
    return f'{str_value[:length]}...'


@register.filter
def provider_icon(provider_name):
    """
    Get Material Icon for payment provider.
    
    Usage:
    {{ payment.provider|provider_icon }}
    """
    provider_icons = {
        'nowpayments': 'account_balance',
        'stripe': 'credit_card',
        'paypal': 'payment',
        'cryptapi': 'currency_bitcoin',
        'cryptomus': 'currency_exchange'
    }
    
    return provider_icons.get(provider_name.lower(), 'account_balance')


@register.filter
def currency_icon(currency_code):
    """
    Get Material Icon for currency.
    
    Usage:
    {{ payment.currency.code|currency_icon }}
    """
    currency_icons = {
        'USD': 'attach_money',
        'EUR': 'euro',
        'GBP': 'currency_pound',
        'BTC': 'currency_bitcoin',
        'ETH': 'currency_exchange',
        'LTC': 'currency_exchange',
        'XRP': 'currency_exchange'
    }
    
    return currency_icons.get(currency_code.upper(), 'currency_exchange')


@register.inclusion_tag('payments/components/status_card.html')
def status_card(title, value, icon='analytics', color_class='text-gray-900 dark:text-white', 
                description='', icon_bg_color='blue', status_icon='', action_url='', action_icon='open_in_new'):
    """
    Render a status card component.
    
    Usage:
    {% status_card 'Active Payments' payment_count 'payments' 'text-blue-600' 'Currently processing' %}
    """
    return {
        'title': title,
        'value': value,
        'icon': icon,
        'color_class': color_class,
        'description': description,
        'icon_bg_color': icon_bg_color,
        'status_icon': status_icon,
        'action_url': action_url,
        'action_icon': action_icon
    }


@register.inclusion_tag('payments/components/provider_card.html')
def provider_card(provider):
    """
    Render a provider card component.
    
    Usage:
    {% provider_card provider_data %}
    """
    return {'provider': provider}


@register.inclusion_tag('payments/components/loading_spinner.html')
def loading_component(size='md', text='Loading...'):
    """
    Render a loading spinner component.
    
    Usage:
    {% loading_component %}
    {% loading_component 'lg' 'Processing payment...' %}
    """
    return {
        'size': size,
        'text': text
    }


@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    """
    Check if current URL matches the given URL name.
    
    Usage:
    <a href="{% url 'payments:dashboard' %}" class="{% active_nav 'payments:dashboard' %}">
    """
    request = context.get('request')
    if not request:
        return ''
    
    try:
        from django.urls import reverse, resolve
        current_url = resolve(request.path_info).url_name
        target_url = url_name.split(':')[-1]  # Get the last part after ':'
        
        if current_url == target_url:
            return 'text-blue-600 bg-blue-50 dark:bg-blue-900 dark:text-blue-200'
        else:
            return 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
    except:
        return 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'


@register.simple_tag
def percentage(value, total):
    """
    Calculate percentage.
    
    Usage:
    {% percentage successful_payments total_payments %}%
    """
    try:
        if not total or total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def multiply(value, arg):
    """
    Multiply two values.
    
    Usage:
    {{ amount|multiply:exchange_rate }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """
    Divide two values.
    
    Usage:
    {{ total_amount|divide:payment_count }}
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0








