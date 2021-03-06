#!/usr/bin/env python
#-*- coding: utf-8 -*-
#=============================================================================
#     FileName:
#         Desc:
#       Author: 苦咖啡
#        Email: voilet@qq.com
#     HomePage: http://blog.kukafei520.net
#      Version: 0.0.1
#      History:
#=============================================================================

import json,time,urllib
from django.shortcuts import render_to_response
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from server_idc.models import  Host,IDC,Server_System,Cores,System_os,system_arch,MyForm,System_usage
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf

from django.contrib.auth.models import User
from salt_ui.api.salt_https_api import salt_api_jobs,pxe_api
from mysite.settings import  salt_api_pass,salt_api_user,salt_api_url
from server_idc.idc_edit_log.idc_log import idc_log

class Host_from(forms.ModelForm):
    FAVORITE_COLORS_CHOICES = MyForm.objects.values_list("id", "service_name")
    business = forms.MultipleChoiceField(required=False,
        widget=forms.CheckboxSelectMultiple, choices=FAVORITE_COLORS_CHOICES)
    class Meta:
        model = Host

@login_required
@csrf_protect
def Index_add(request):
    content = {}
    if request.method == 'POST':    #验证post方法
        uf = Host_from(request.POST)   #绑定POST动作
        node_name = request.POST.getlist("node_name")
        operating = request.POST.getlist("system")
        mac = request.POST.getlist("mac")
        model = request.POST.getlist("brand")
        usage = request.POST.getlist("usage")
        # create_time = time.strftime('%Y-%m-%d',time.localtime(time.time())) # %H:%M:%S
        if uf.is_valid(): #验证数据有效性
            # u'''向pxe提交数据'''
            # pxe_data = pxe_api({
            #     "hostname":node_name[0].encode("utf8"),
            #     "operating":operating[0].encode("utf8").lower() + "_6u4_64",
            #     "mac":mac[0].encode("utf8"),
            #     "usage":usage[0].encode("utf8"),
            #     "model":model[0].encode("utf8").lower(),
            # },pxe_url_api)
            # pxe_post_data = json.load(pxe_data.run())
            # if pxe_post_data["status"] !=200:
            #     print "is over"
            #     return render_to_response('server_idc/index.html',content,context_instance=RequestContext(request))
            # else:
            uf.save()
            """
            如果commit为False,则ManyToMany就需要使用以下方法
            """
            zw = uf.save(commit=False)
            zw.edit_username = request.user.username
            zw.save()
            uf.save_m2m()
            uf = Host_from()
            content['uf'] = uf
            content.update(csrf(request))
            return render_to_response('server_idc/index.html',content,context_instance=RequestContext(request))
        else:
            print "save error"
            uf = Host_from()
            content["server_type"] = MyForm.objects.all()
            content['uf'] = uf
            content.update(csrf(request))
            return render_to_response('server_idc/index.html',content,context_instance=RequestContext(request))
    else:
        uf = Host_from()
        content['uf'] = uf
        content["server_type"] = MyForm.objects.all()
        content.update(csrf(request))
        return render_to_response('server_idc/index.html',content,context_instance=RequestContext(request))

@login_required
@csrf_protect
def services_list_all(request):
    content = {}
    server_list = Host.objects.order_by("-id")
    server_type = MyForm.objects.all()
    content["server_type"] = server_type
    content["list"] = server_list
    content.update(csrf(request))
    # return render_to_response('server_idc/list_test.html',content,context_instance=RequestContext(request))
    return render_to_response('server_idc/list.html',content,context_instance=RequestContext(request))

@login_required
@csrf_protect
def services_install_all(request):
    content = {}
    server_list = Host.objects.filter(auto_install=0).order_by("-id")
    server_type = MyForm.objects.all()
    content["server_type"] = server_type
    content["list"] = server_list
    content.update(csrf(request))
    # return render_to_response('server_idc/list_test.html',content,context_instance=RequestContext(request))
    return render_to_response('server_idc/install_list.html',content,context_instance=RequestContext(request))

@login_required
@csrf_protect
def services_install_error(request):
    content = {}
    server_list = Host.objects.filter(auto_install=2).order_by("-id")
    server_type = MyForm.objects.all()
    content["server_type"] = server_type
    content["list"] = server_list
    content.update(csrf(request))
    # return render_to_response('server_idc/list_test.html',content,context_instance=RequestContext(request))
    return render_to_response('server_idc/install_error.html',content,context_instance=RequestContext(request))

@login_required
@csrf_protect
def services_list_id(request,id):
    content = {}
    server_list = Host.objects.get(id = id)
    server_type = MyForm.objects.all()
    content["server_type"] = server_type
    content["list"] = server_list
    content.update(csrf(request))
    # return render_to_response('server_idc/list_test.html',content,context_instance=RequestContext(request))
    return render_to_response('server_idc/list_id.html',content,context_instance=RequestContext(request))

@login_required
@csrf_protect
def server_edit(request,id):
    content = {}
    edit_id = Host.objects.get(id = id)
    #机房名称
    idc_name = IDC.objects.all()
    server_type = MyForm.objects.all()
    if request.method == 'POST':    #验证post方法
        uf = Host_from(request.POST)   #绑定POST动作
        if uf.is_valid(): #验证数据有效性
            uf.auto_id = edit_id.id
            zw = uf.save(commit=False)
            zw.edit_username = request.user.username
            zw.old_editname = edit_id.edit_username
            zw.old_editdatetime = edit_id.edit_datetime
            zw.auto_install = edit_id.auto_install
            zw.id=edit_id.id
            zw.create_time = edit_id.create_time
            zw.save()
            uf.save_m2m()
            print "保存数据"
            idc_log(request.user.username, edit_id.node_name, "修改", edit_id.edit_username, edit_id.edit_datetime, id, request.user.id)
            return HttpResponseRedirect('/assets/list_id/'+ id )
            # return render_to_response('server_idc/edit.html',content,context_instance=RequestContext(request))
        else:
            print "is over"
            print uf.is_valid()
    else:
        uf = Host_from()
        content["uf"] = uf
        content["edit_brand"] = Server_System
        content["edit_Cores"] = Cores
        content["edit_system"] = System_os
        content["edit_system_cpuarch"] = system_arch
        content["server_type"] = server_type
        content["edit_id"] = edit_id
        content["server_name"] = idc_name
        content["edit_usage"] = System_usage
        content.update(csrf(request))
        return render_to_response('server_idc/edit.html', content, context_instance=RequestContext(request))

#更新

#按服务排序
@login_required
@csrf_protect
def server_type_list(request,id):
    content = {}
    business_name = MyForm.objects.get(id=id)
    server_list = business_name.host_set.all()
    server_user_all = business_name.service_user.all()
    # user = request.user.myform_set.all()
    content["server_type"] = MyForm.objects.all()
    content["list"] = server_list
    content["server_user_all"] = server_user_all
    content["business_name"] = business_name
    if len(content['list']) >0:
        content["test_error"] = True
    else:
        content["test_error"] = False
    content.update(csrf(request))

    return render_to_response('server_idc/server_type.html', content, context_instance=RequestContext(request))


class Service_type_from(forms.ModelForm):
    FAVORITE_COLORS_CHOICES = User.objects.values_list("id", "username",)
    service_user = forms.MultipleChoiceField(required=False,
        widget=forms.CheckboxSelectMultiple, choices=FAVORITE_COLORS_CHOICES)
    class Meta:
        model = MyForm

#业务管理
@login_required
@csrf_protect
def server_type_add(request):
    content = {}
    if request.method == 'POST':    #验证post方法
        uf = Service_type_from(request.POST)   #绑定POST动作
        print uf
        if uf.is_valid(): #验证数据有效性
            uf.save()
            uf = Service_type_from()
            content['uf'] = uf
            content["server_type"] = MyForm.objects.all()
            content["user_list"]=User.objects.all()
            content.update(csrf(request))
            print "server_type save is ok"
            # return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))
            return HttpResponseRedirect("/assets/server/type/list/")
        else:
            print "save error"
            uf = Service_type_from()
            content["server_type"] = MyForm.objects.all()
            content['uf'] = uf
            content.update(csrf(request))
            return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))
    else:
        uf = Service_type_from()
        content['uf'] = uf
        content["user_list"]=User.objects.all()
        content["server_type"] = MyForm.objects.all()
        content.update(csrf(request))
        return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))

#业务管理
@login_required
@csrf_protect
def auth_server_type_list(request):
    content = {}
    if request.method == 'POST':    #验证post方法
        uf = Service_type_from(request.POST)   #绑定POST动作
        if uf.is_valid(): #验证数据有效性
            uf.save()
            uf = Service_type_from()
            content['uf'] = uf
            content["server_type"] = MyForm.objects.all()
            content.update(csrf(request))
            return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))
        else:
            print "save error"
            uf = Service_type_from()
            content["server_type"] = MyForm.objects.all()
            content['uf'] = uf
            content.update(csrf(request))
            return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))
    else:
        business_name = MyForm.objects.all().order_by("-id")
        list_api_return = []
        for i in business_name:
            server_list = i.host_set.all()
            server_user_all = i.service_user.all()
            user = request.user.myform_set.all()
            content["server_type"] = MyForm.objects.all()
            content["list"] = server_list
            content["server_user_all"] = server_user_all
            content["business_name"] = business_name
            list_api_return.append({"server_user_all":server_user_all, "server_type":i, "type_id":i.id})
        try:
            if len(content['list']) >0:
                content["test_error"] = True
            else:
                content["test_error"] = False
        except KeyError:
            content["test_error"] = False
        content["list_server_type"] = list_api_return
        content["server_type"] = MyForm.objects.all()
        content.update(csrf(request))
        return render_to_response('server_idc/server_type_list.html', content, context_instance=RequestContext(request))

#业务修改
@login_required
@csrf_protect
def auth_server_type_edit(request,id):
    business_name = MyForm.objects.get(id=id)
    content = {}
    server_type_user = []
    if request.method == 'POST':    #验证post方法
        uf = Service_type_from(request.POST)   #绑定POST动作
        if uf.is_valid(): #验证数据有效性
            zw = uf.save(commit=False)
            zw.id = business_name.id
            zw.save()
            uf.save_m2m()
            uf = Service_type_from()
            content['uf'] = uf
            content["server_type"] = MyForm.objects.all()
            content.update(csrf(request))
            # return render_to_response('server_idc/server_type_add.html',content,context_instance=RequestContext(request))
            return HttpResponseRedirect("/assets/server/server_type/" + id + "/")
        else:
            print "save error"
            uf = Service_type_from()
            content["server_type"] = MyForm.objects.all()
            content['uf'] = uf
            content.update(csrf(request))
            return render_to_response('server_idc/server_type_add.html', content, context_instance=RequestContext(request))
    else:
        user_all = User.objects.all()
        server_list = business_name.host_set.all()
        server_user_all = business_name.service_user.values("first_name")
        content["server_type"] = MyForm.objects.all()
        content["list"] = server_list
        content["user_all"] = user_all
        content["server_user_all"] = server_user_all
        content["business_name"] = business_name
        content["server_type"] = MyForm.objects.all()

        for i in server_user_all:
            server_type_user.append(str(i["first_name"]).encode("utf-8"))
        content["server_type_user"] = server_type_user
        content.update(csrf(request))
        return render_to_response('server_idc/server_type_edit.html', content, context_instance=RequestContext(request))

@login_required
@csrf_protect
def server_id_delete(request,id):
    content = {}
    edit_id = Host.objects.get(id = id)
    #机房名称
    idc_name = IDC.objects.all()
    server_type = MyForm.objects.all()
    if request.method == 'POST':    #验证post方法
        uf = Host_from(request.POST)   #绑定POST动作
        delete_id = request.POST.getlist("delete_id")
        delete_id = int(delete_id[0])
        delete_name = request.POST.getlist("delete_name")
        for i in delete_name:
            print i
        Host.objects.get(id=delete_id).delete()
        idc_log(request.user.username, edit_id.node_name,"删除", edit_id.edit_username, edit_id.edit_datetime, id, request.user.id)
        return HttpResponseRedirect("/assets/server/type/notid/")
    else:
        content["edit_brand"] = Server_System
        content["edit_Cores"] = Cores
        content["edit_system"] = System_os
        content["edit_system_cpuarch"] = system_arch
        content["server_type"] = server_type
        content["edit_id"] = edit_id
        content["server_name"] = idc_name
        content["edit_usage"] = System_usage
        content.update(csrf(request))
        return render_to_response('server_idc/delete.html', content, context_instance=RequestContext(request))