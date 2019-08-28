import datetime
import decimal

from django import forms
from django.utils.encoding import python_2_unicode_compatible
from django.template.defaultfilters import truncatewords_html, linebreaksbr
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.dateformat import format
from django.conf import settings

from djangoplus.templatetags.djangoplus_tags import moneyformat

DEBUG = False

class ReadOnlyTextWidget(forms.widgets.Widget):
    """
    This is DefaultValueWidget 
    from http://www.djangosnippets.org/snippets/323/
    """
    choices = None
    initial = None
    show_input = True
    decimal_places = 2
    link = None

    def __init__(self, value=None, display=None, attrs=None, object=None,
            choices=None, show_input=True, decimal_places=2):
        if isinstance(display, forms.ModelChoiceField):
            try:
                self.display = display.queryset.get(pk=value)
            except:
                self.display = value
        # this allows to genericly pass in any field object intending to
        # catch ModelChoiceFields, without having to care about the actual
        # type.
        elif isinstance(display, forms.Field):
            self.display = None
        else:
            self.display = display

        self.value = value
        self.object = object
        self.choices = choices
        self.show_input = show_input
        self.decimal_places = decimal_places

        super(ReadOnlyTextWidget, self).__init__(attrs)    

    def value_from_datadict(self, data, files, name):
        value = data.get(name, self.value)
        if DEBUG: print("[d] value for %s = %s") % (name, value)
        #HACK: Decimal can't be converted to Decimal again
        # so returning str instead
        if type(value) is decimal.Decimal: return str(value)
        if isinstance(value, forms.Field): return str(value)
        return value
        
    def render(self, name, value, attrs=None):
        # Formats decimal value with period instead dot if moneyformat does it
        if isinstance(value, decimal.Decimal):
            value = moneyformat(value, self.decimal_places)

        if self.display is None: 
            if self.object:
                method_name = 'get_%s_value'%name
                r = getattr(self.object, name)
                if hasattr(self.object, method_name):
                    r = getattr(self.object, method_name)(r)
            else:
                r = value
        else: 
            r = self.display

        try:
            display = getattr(self.object, 'get_%s_display'%name)()
        except AttributeError:
            if type(r) == datetime.date:
                value = display = format(r, settings.DATE_FORMAT)
            elif type(r) == datetime.datetime:
                value = display = format(r, settings.DATETIME_FORMAT)
            elif self.choices:
                display = dict(self.choices).get(value, value)
            else:
                s = force_unicode(r, strings_only=False)
                display = truncatewords_html(linebreaksbr(s), 50)

        if isinstance(value, models.Model):
            value = value.pk

        # Shows the link
        link = self.link and '<a href="%s">Ver mais...</a>'%self.link or ''

        # Avoid "None" value on front end
        display = display != 'None' and display or ''

        # Avoid None value
        value = value is not None and value or ''

        return mark_safe('<span class="value read-only-widget">%s %s</span> <input type="hidden" name="%s" value="%s" id="%s">'%(
            display, link, self.show_input and name or '', value, attrs.get('id', 'id_'+name)
            ))


class ReadOnlyAdminMixin(object):
    """Disables all editing capabilities."""
    change_form_template = "admin/view.html"

    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdminMixin, self).__init__(*args, **kwargs)
        self.readonly_fields = self.model._meta.get_all_field_names()

    def get_actions(self, request):
        actions = super(ReadOnlyAdminMixin, self).get_actions(request)
        del actions["delete_selected"]
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        pass

    def delete_model(self, request, obj):
        pass

    def save_related(self, request, form, formsets, change):
        pass