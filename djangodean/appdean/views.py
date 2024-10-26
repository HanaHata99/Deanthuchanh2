from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pgsql

def listview(request):
    template = loader.get_template('viewdata.html')
    datas = []
    with pgsql.Connection(("localhost", 5432), "postgres", "12345", "postgres", tls = False) as db:
        statement = db.prepare("SELECT * FROM dulieudean LIMIT 1000")
        datas = list(statement())
        
        statement.close()

    context = {
        'mymembers': datas,
    }
    return HttpResponse(template.render(context, request))

def detailview(request):
    template = loader.get_template('viewdetail.html')
    A = request.GET.get('q', 'default')
    with pgsql.Connection(("localhost", 5432), "postgres", "12345", "postgres", tls = False) as db:

        with db.prepare("SELECT * FROM dulieudean where batch_id = $1") as person:
            detail = person(A).row()
            print(detail)
        

    context = {
        'detail': detail,
    }
    return HttpResponse(template.render(context, request))
