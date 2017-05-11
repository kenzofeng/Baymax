from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from models import Project,Job,Run_Status,Job_Test,Log,build,Map
import json
import jenkins
from datetime import *
import os
import env
import utility


def job_create(request,project):
#     project =  request.GET['p']
#     logdir = datetime.utcnow().strftime('%Y%m%d')
#     p = Project.objects.get(pk=project)
#     utility.mklogdir(logdir)
#     job = Job(project=project,status='w',start_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
#               job_number="",email=p.email)
#     job.save()
#     log = Log()
#     log.job = job
#     log.path = "%s/%s.log"%(logdir,datetime.utcnow().strftime('%H%M%S'))
#     log.save()
    print project
#     return HttpResponse(json.dumps({'jobid':job.id,'log':"http://%s/regression/log/%s"%(request.get_host(),job.id)}),content_type='application/json')
    return HttpResponse(json.dumps({'project':project}))

def job_start(request,jobid):
    job = None
    try:
        job = Job.objects.get(pk=jobid)
        job.starts(request.get_host())
        job.status='d'
        job.save()
        job.save_log()
        results = job.get_results()
        return HttpResponse(results,content_type='application/json')
    except Exception,e:
        job.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        job.status='e'
        job.save()
        utility.logmsg(job.log.path,str(e))
        job.save_log()
        return HttpResponse(str(e))

def job_log_ex(reuqest,jobid):
    job = Job.objects.get(pk=jobid)
    fst = ''
    try:
        logpath = os.path.join(env.log,job.log.path)
        if os.path.exists(logpath):
            f = open(logpath,'r')
            fst = f.read()
            f.close()
    except Exception:
        pass
    return HttpResponse(fst,content_type='text/html') 

def job_log(request,jobid):
    job = Job.objects.get(pk=jobid)
    log = job.log.text
    joblog = ''
    if log is not None:
        for l in log.split('\n'):
            joblog  = joblog+"<span>%s</span><br/>"%(l.encode("gbk"))
        return HttpResponse(joblog,content_type='text/html')
    else:
        try:
            logpath = os.path.join(env.log,job.log.path)
            if os.path.exists(logpath):
                f = open(logpath,'r')
                fst = f.read()
                f.close()
                for l in fst.split('\n'):
                    joblog  = joblog+"<span>%s</span><br/>"%(l.encode("gbk"))
        except Exception:
            pass
    return HttpResponse(joblog,content_type='text/html') 
        
def test_log(request,logid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report,test.report,env.log_html)
    f=open(path)
    return HttpResponse(f.read(),content_type='text/html')

def test_report(request,logid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report,test.report,env.report_html)
    f=open(path)
    return HttpResponse(f.read(),content_type='text/html')
    
def test_compare(request,logid,cid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report,test.report,cid)
    f=open(path)
    return HttpResponse(f.read(),content_type='text/html')


def test_redfile(request,logid,redfile):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report,test.report,env.deps,redfile)
    f=open(path)
    return HttpResponse(f.read(),content_type='text/css')

def testproject(request):
    return render(request,'regression/testproject.html')

@csrf_exempt
def testproject_add(request):
    name = request.POST['name']
    p = Project()
    p.name = name
    p.save()
    return HttpResponse(json.dumps({'status':'scuess'}),content_type='application/json') 

@csrf_exempt
def testproject_update(request):
    try:
        mb=build.objects.get(project=request.POST['pk'])
        mb.build_command = request.POST['build']
        mb.save()
    except Exception:
        mb = build()
        mb.project = request.POST['name']
        mb.build_command = request.POST['build']
        mb.save()
        
    maps = Map.objects.filter(project=request.POST['pk'])
    for m in maps:
        m.delete()
        
    maptest="map-test-"
    mapurl="map-url-"
    mapwar="map-war-"
    maprobot="map-robot-"
    for key in request.POST:
        kid  = (key.split('-'))[-1]
        if key.find(maptest) != -1:
            m = Map()
            m.project=request.POST['pk']
            m.test= request.POST['%s%s'%(maptest,kid)]
            m.testurl=request.POST['%s%s'%(mapurl,kid)]
            m.war = request.POST['%s%s'%(mapwar,kid)]
            m.robot_parameter= request.POST['%s%s'%(maprobot,kid)]
            m.save()
    
    p = Project.objects.get(pk=request.POST['pk'])
    p.name = request.POST['name']
    p.scm = request.POST['scm']
    p.devurl = request.POST['url']
    p.email = request.POST['email']
    p.branch=request.POST['branch']
    p.save()
    return HttpResponse(json.dumps({'status':'scuess'}),content_type='application/json')

@csrf_exempt
def testproject_delete(request):
    p = Project.objects.get(pk=request.POST['pk'])
    try:
        mb=build.objects.get(project=request.POST['pk'])
        mb.delete()
    except Exception:
        pass
    maps = Map.objects.filter(project=request.POST['pk'])
    for m in maps:
        m.delete()
    p = Project.objects.get(pk=request.POST['pk'])
    p.delete()
    return HttpResponse(json.dumps({'status':'scuess'}),content_type='application/json')

def testproject_getall(request):
    list_project = Project.objects.all()
    return HttpResponse(serializers.serialize("json", list_project),content_type='application/json')

def testproject_testproject(request):
    tid = request.GET['tid']
    project = Project.objects.get(pk=tid)
    json = project.toJSON()
    return HttpResponse(json,content_type='application/json')

def scm_testproject(request):
    SCM={'scms':[{'name':'svn'},{'name':'git'}]}
    return HttpResponse(json.dumps(SCM),content_type='application/json')