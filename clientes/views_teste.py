# -*- coding: utf-8 -*-

import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
def testando(request):
    u"""
    Reseta a senha do funcionário dado.
    """

    funcionario_pk = request.POST['funcionario_pk']

    ret = {
        'res':'no',
        'funcionario_pk': funcionario_pk,
    }
    
    return HttpResponse(json.dumps(ret), content_type='application/json')
