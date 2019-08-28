# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from functools import wraps, update_wrapper
        

def permitido(perms):
    def _inner(func):
        def _wrapper(request, *args, **kwargs):
            # Verifica se o user tem permissão
            #raise Exception( request.user.perms )
            if not request.user.has_perm(perms):
                messages.info(request, u'Vocẽ não tem permissão.')
                return HttpResponseRedirect('/')

            # Caso tenha permissão
            return func(request, *args, **kwargs)
        return _wrapper
    return _inner


def method_decorator(decorator):
    """Converts a function decorator into a method decorator.
    
    This works properly for both: decorators with arguments and without them. The Django's version
    of this function just supports decorators with no arguments."""

    # For simple decorators, like @login_required, without arguments
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            def bound_func(*args2, **kwargs2):
                return func(self, *args2, **kwargs2)
            return decorator(bound_func)(*args, **kwargs)
        return wraps(func)(_wrapper)

    # Called everytime
    def _args(*argsx, **kwargsx):
        # Detect a simple decorator and call _dec for it
        if len(argsx) == 1 and callable(argsx[0]) and not kwargsx:
            return _dec(argsx[0])

        # Used for decorators with arguments, like @permission_required('something')
        def _dec2(func):
            def _wrapper(self, *args, **kwargs):
                def bound_func(*args2, **kwargs2):
                    return func(self, *args2, **kwargs2)
                return decorator(*argsx, **kwargsx)(bound_func)(*args, **kwargs)
            return wraps(func)(_wrapper)
        return _dec2

    update_wrapper(_args, decorator)
    # Change the name to aid debugging.
    _args.__name__ = 'method_decorator(%s)' % decorator.__name__
    return _args

login_required_m = method_decorator(login_required)
permission_required_m = method_decorator(permission_required)

def page(template=None, context=None, **decorator_args):
    """This decorator was made by Yuri Baburov at its first version and Marinho just improved it"""
    def _wrapper(fn):
        def _innerWrapper(*args, **kw):
            # Supports independent function views
            if isinstance(args[0], HttpRequest):
                request = args[0]

            # Supports ModelAdmin method views
            elif isinstance(args[0], ModelAdmin):
                model_admin = args[0]
                request = args[1]

            context_dict = decorator_args.copy()
            template = kw.pop("template", _innerWrapper.template)
            g = fn(*args, **kw)
            if issubclass(type(g), HttpResponse): 
                return g
            if not hasattr(g, 'next'):  #Is this a generator?  Otherwise make it a tuple!
                g = (g,)
            for i in g:
                if issubclass(type(i), HttpResponse):
                    return i
                if type(i) == type(()):
                    context_dict[i[0]] = i[1]
                else:
                    context_dict.update(i)
            template_name = context_dict.get("template", template)
            
            context_instance = context_dict.get("context", context)
            if not context_instance:
                context_instance = RequestContext(request, context_dict)
            return render_to_response(template_name, context_dict, context_instance)

        _innerWrapper.template = template
        return _innerWrapper
    return _wrapper

