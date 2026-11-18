/* Initialises our select2 widgets (geo, currency, location): elements with class
 * `cfg-autocomplete`. select2 itself is the copy that ships with contrib.admin;
 * it reads the `data-ajax--*`, `data-placeholder` and `data-allow-clear` attributes. */
'use strict';
{
    const $ = django.jQuery;

    const init = (root) => {
        $(root).find('.cfg-autocomplete').each((_i, element) => {
            if (element.id.match(/__prefix__/) || $(element).hasClass('select2-hidden-accessible')) {
                return;
            }
            $(element).select2();
        });
    };

    $(() => init(document));
    document.addEventListener('formset:added', (event) => init(event.target));
}
