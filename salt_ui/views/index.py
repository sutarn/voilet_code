#coding=UTF-8
import datetime
import os
import re
#import md5
import json

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.template import RequestContext
from django.db import connection
from django.http import HttpResponse
#from salt_ui.api import salt_api
from salt_ui.models import *
from django.contrib.auth.decorators import login_required
import commands,json,yaml
import subprocess
from salt_ui.api import *
from server_idc.models import  Host,IDC,Server_System,Cores,System_os,system_arch,MyForm
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from salt_ui.api.salt_token_id import salt_api_token
from salt_ui.api.salt_token_id import *



#songxs add
@login_required
def salt_index(request):
    return render_to_response('saltstack/salt_index.html',context_instance=RequestContext(request))

@login_required
def salt_status(request,id):
    context = {}
    id = int(id)
    service_user = request.user.myform_set.all()
    context['service_name'] = service_user
    if id == 1:
        token_api_id = token_id()
        list = salt_api_token(
        {
        "client":'runner',
        "fun":"manage.status",
                   },
        "https://192.168.49.14/",
        {"X-Auth-Token": token_api_id}
        )
        master_status =list.run()
        master_status = master_status["return"]
        for i in master_status:
            context['down']= i["down"]
            context['up']= i['up']
            context["live"] = len(i['up'])
            context["live_down"] = len(i['down'])
        context.update(csrf(request))
        return render_to_response('saltstack/salt_status.html',context,context_instance=RequestContext(request))
    if id == 2:
        token_api_id = token_id()
        list = salt_api_token(
        {
        "client":'local',
        "fun":"test.ping",
        "tgt":"*"
                   },
        "https://192.168.49.14/",
        {"X-Auth-Token": token_api_id}
        )
        list = list.run()
        context["salt_key"]=list["return"]
        context.update(csrf(request))
        return render_to_response('saltstack/salt_key.html',context,context_instance=RequestContext(request))
    if id == 3:
        context.update(csrf(request))
        return render_to_response('saltstack/salt_cmd.html',context,context_instance=RequestContext(request))

@login_required
@csrf_protect
def salt_cmd(request):
    context = {}
    type_node = ""
    if request.method == 'POST':
        salt_text = request.POST
        service_type = salt_text.getlist("business")
        for i in service_type:
            service_name_type = get_object_or_404(MyForm,service_name = i)
            test = service_name_type.host_set.all()
            for s in test:
                type_node += "%s," % (s.node_name)
        context["type_node"] = type_node
        if salt_text['salt_cmd']:
            salt_cmd_lr = salt_text['salt_cmd']
            salt_node_name = salt_text["salt_node_name"]
            # if salt_node_name:
            token_api_id = token_id()
            list_all = salt_api_token(
            {
            'client': 'local',
            'fun': 'cmd.run',
            'tgt':salt_node_name,
            'arg':salt_cmd_lr ,
                           },
            "https://192.168.49.14/",
            {"X-Auth-Token": token_api_id}
            )
            list_all = list_all.run()
            for i in list_all["return"]:
                context["cmd_run"] = i
            context["cmd_Advanced"]=False
            context["salt_cmd"]=salt_text['salt_cmd']
            context.update(csrf(request))
            return render_to_response('saltstack/salt_cmd_run.html',context,context_instance=RequestContext(request))
            #     #return HttpResponse(json.dumps(cmd))
        else:
            return render_to_response('saltstack/salt_cmd_run.html',context,context_instance=RequestContext(request))

@login_required
@csrf_protect
def salt_garins(request):
    context = {}
    if request.method == 'POST':
        salt_text = request.POST
        if salt_text['salt_cmd']:
            salt_cmd_lr = salt_text['salt_cmd']
            salt_node_name = salt_text["salt_node_name"]
            # if salt_node_name:
            token_api_id = token_id()
            list_all = salt_api_token(
            {
            'client': 'local',
            'fun': 'cmd.run',
            'tgt':salt_node_name,
            'arg':salt_cmd_lr ,
                           },
            "https://192.168.49.14/",
            {"X-Auth-Token": token_api_id}
            )
            list_all = list_all.run()
            for i in list_all["return"]:
                context["cmd_run"] = i
            context["cmd_Advanced"]=False
            context["salt_cmd"]=salt_text['salt_cmd']
            context.update(csrf(request))
            return render_to_response('saltstack/salt_cmd_grains_run.html',context,context_instance=RequestContext(request))
            #     #return HttpResponse(json.dumps(cmd))
        #if salt_text['salt_cmd']:
        #    client = salt_api.client
        #    salt_cmd_lr = salt_text['salt_cmd']
        #    salt_cmd_context = salt_cmd_lr.partition("@")
        #    salt_cmd_context = list(salt_cmd_context)
        #    salt_cmd_len = salt_cmd_lr.split("@")
        #    if len(salt_cmd_len) >1 :
        #        cmd = client.cmd( salt_cmd_context[0], 'grains.item', [salt_cmd_context[2]] )
        #        context["cmd_run"]=cmd
        #        context["cmd_Advanced"]=False
        #        context["salt_cmd"]=salt_text['salt_cmd']
        #        context.update(csrf(request))
        #        # salt_jid
        #        return render_to_response('saltstack/salt_cmd_grains_run.html',context,context_instance=RequestContext(request))
        #    else:
        #        cmd = client.cmd(salt_text['salt_cmd'].strip(), 'grains.items')
        #        context['cmd_run'] = cmd
        #        context["cmd_Advanced"]=True
        #        context['salt_cmd'] = salt_text['salt_cmd']
        #        context.update(csrf(request))
        #        return render_to_response('saltstack/salt_cmd_grains_run.html',context,context_instance=RequestContext(request))
        #else:
        #    return render_to_response('saltstack/salt_cmd_grains_run.html',context,context_instance=RequestContext(request))
    else:
        context.update(csrf(request))
        return render_to_response('saltstack/salt_garins.html',context,context_instance=RequestContext(request))

#自动化部署
@login_required
@csrf_protect
def salt_nginx(request):
     context = {}
     return render_to_response('saltstack/salt_cmd_run.html',context,context_instance=RequestContext(request))

#系统初始化
@login_required
@csrf_protect
def salt_check_install(request):
     context = {}
     if request.method == 'POST':
        salt_text = request.POST
        return render_to_response('saltstack/salt_check_install.html',context,context_instance=RequestContext(request))
     else:
         server_list = open("/srv/salt/check_install/hostname.jinja","r")
         server = server_list.read()
         server_list.close()
         server_node = open("/etc/salt/roster","r")
         node = server_node.read()
         server_node.close()
         context["server"] = server
         context["node"] = node
         context["cmd_Advanced"]=True
         context.update(csrf(request))
         return render_to_response('saltstack/salt_check_install.html',context,context_instance=RequestContext(request))

#jinja
@login_required
@csrf_protect
def salt_check_jinja(request):
     context = {}
     if request.method == 'POST':
        salt_text = request.POST
        context.update(csrf(request))
        server_list = open("/srv/salt/check_install/hostname.jinja","w")
        server_list.write(salt_text['salt_content_jinja'])
        server_list.close()
        context["cmd_Advanced"] = True
        return render_to_response('saltstack/salt_check_over.html',context,context_instance=RequestContext(request))



#salt_node
@login_required
@csrf_protect
def salt_check_node(request):
     context = {}
     if request.method == 'POST':
        salt_text = request.POST
        context.update(csrf(request))
        server_list = open("/etc/salt/roster","w")
        server_list.write(salt_text['salt_content_node'])
        server_list.close()
        context["server_list"] = server_list
        context["cmd_Advanced"] = True
        return render_to_response('saltstack/salt_check_over.html',context,context_instance=RequestContext(request))

#salt_node_shell
@login_required
@csrf_protect
def salt_check_setup(request):
     context = {}
     if request.method == 'POST':
        salt_text = request.POST
        #client = salt_api.client
        salt_cmd_lr = salt_text['salt_shell_node']
        cmd = commands.getoutput("salt-ssh " + salt_cmd_lr + " state.sls check_install" )
        context['salt_cmd'] = cmd
        context["cmd_Advanced"] = True
        context.update(csrf(request))
        return render_to_response('saltstack/salt_check_setup.html',context,context_instance=RequestContext(request))


#salt_node_shell
@login_required
@csrf_protect
def salt_state_sls(request):
     context = {}
     if request.method == 'POST':
        salt_text = request.POST
        salt_cmd_lr = salt_text['salt_sls']
        node = salt_text["salt_node"]
        shell = "salt \"{node}\" state.sls \"{salt_cmd_lr}\"".format(node=node,salt_cmd_lr=salt_cmd_lr)
        cmd = commands.getoutput(shell)
        context['salt_cmd'] = cmd
        context["cmd_Advanced"] = True
        context.update(csrf(request))
        return render_to_response('saltstack/salt_check_setup.html',context,context_instance=RequestContext(request))
     else:
         context["cmd_Advanced"] = False
         context.update(csrf(request))
         return render_to_response('saltstack/salt_state_sls.html',context,context_instance=RequestContext(request))