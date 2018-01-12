from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import zlib
import os
from engine import env
from engine.job import *
from models import Job_Test, Map, Test_Log, Job
from engine import utility


def job_start(request, project):
    try:
        results = start(request, project)
        return HttpResponse(results, content_type='application/json')
    except Exception, e:
        return HttpResponse(e)


def job_log_ex(reuqest, jobid):
    job = Job.objects.get(pk=jobid)
    fst = ''
    try:
        logpath = os.path.join(env.log, job.log.path)
        if os.path.exists(logpath):
            f = open(logpath, 'r')
            fst = f.read()
            f.close()
    except Exception, e:
        return HttpResponse(e)
    return HttpResponse(fst, content_type='text/html')


def test_run_log(request, logid):
    test_log = Test_Log.objects.get(pk=logid)
    log = test_log.text
    joblog = ''
    if log is not None:
        try:
            log = zlib.decompress(log.decode("base64"))
        except Exception:
            pass
        for l in log.split('\n'):
            joblog = joblog + "<span>%s</span><br/>" % (l)
        return HttpResponse(joblog, content_type='text/html')
    else:
        try:
            logpath = os.path.join(env.log, test_log.path)
            if os.path.exists(logpath):
                f = open(logpath, 'r')
                fst = f.read()
                f.close()
                for l in fst.split('\n'):
                    joblog = joblog + "<span>%s</span><br/>" % (l)
        except Exception, e:
            return HttpResponse(e)
    return HttpResponse(joblog, content_type='text/html')


def job_log(request, jobid):
    job = Job.objects.get(pk=jobid)
    log = job.log.text
    joblog = ''
    if log is not None:
        try:
            log = zlib.decompress(log.decode("base64"))
        except Exception:
            pass
        for l in log.split('\n'):
            joblog = joblog + "<span>%s</span><br/>" % (l)
        return HttpResponse(joblog, content_type='text/html')
    else:
        try:
            logpath = os.path.join(env.log, job.log.path)
            if os.path.exists(logpath):
                f = open(logpath, 'r')
                fst = f.read()
                f.close()
                for l in fst.split('\n'):
                    joblog = joblog + "<span>%s</span><br/>" % (l.encode("gbk"))
        except Exception, e:
            return HttpResponse(e)
    return HttpResponse(joblog, content_type='text/html')


def test_log(request, logid):
    result = ""
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report, env.log_html)
    if os.path.exists(path):
        f = open(path)
        result = f.read()
        f.close()
    return HttpResponse(result, content_type='text/html')


def test_report(request, logid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report, env.report_html)
    f = open(path)
    return HttpResponse(f.read(), content_type='text/html')

def test_cache(request, logid, cid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report,'cache',cid)
    f = open(path)
    return HttpResponse(f.read(), content_type='text')

def test_new_compare(request, logid, cid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report,'compare',cid)
    f = open(path)
    return HttpResponse(f.read(), content_type='text/html')


def test_new_redfile(request, logid, redfile):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report,'compare', env.deps, redfile)
    f = open(path)
    return HttpResponse(f.read(), content_type='text/css')


def test_compare(request, logid, cid):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report, cid)
    f = open(path)
    return HttpResponse(f.read(), content_type='text/html')


def test_redfile(request, logid, redfile):
    test = Job_Test.objects.get(pk=logid)
    path = os.path.join(env.report, test.report, env.deps, redfile)
    f = open(path)
    return HttpResponse(f.read(), content_type='text/css')


def testproject(request):
    return render(request, 'regression/testproject.html')


def testjob(request):
    return render(request, 'regression/job.html')


def testlab(request):
    return render(request, 'regression/lab.html')


@csrf_exempt
def testproject_add(request):
    name = request.POST['name']
    p = Project()
    p.name = name
    p.save()
    return HttpResponse(json.dumps({'status': 'scuess'}), content_type='application/json')


@csrf_exempt
def testproject_update(request):
    maps = Map.objects.filter(project=request.POST['pk'])
    for m in maps:
        m.delete()
    maptest = "map-test-"
    mapurl = "map-url-"
    maprobot = "map-robot-"
    mapuse = 'map-use-'
    for key in request.POST:
        kid = (key.split('-'))[-1]
        if key.find(maptest) != -1:
            m = Map()
            m.project = request.POST['pk']
            m.test = request.POST['%s%s' % (maptest, kid)]
            m.testurl = request.POST['%s%s' % (mapurl, kid)]
            m.robot_parameter = request.POST['%s%s' % (maprobot, kid)]
            if '%s%s' % (mapuse, kid) in request.POST:
                m.use = True
            else:
                m.use = False
            m.save()
    p = Project.objects.get(pk=request.POST['pk'])
    p.name = request.POST['name']
    p.email = request.POST['email']
    p.save()
    return HttpResponse(json.dumps({'status': 'scuess'}), content_type='application/json')


@csrf_exempt
def testproject_delete(request):
    p = Project.objects.get(pk=request.POST['pk'])
    maps = Map.objects.filter(project=request.POST['pk'])
    for m in maps:
        m.delete()
    p = Project.objects.get(pk=request.POST['pk'])
    p.delete()
    return HttpResponse(json.dumps({'status': 'scuess'}), content_type='application/json')


def testjob_getall(request, number):
    list_job = Job.objects.all().order_by('-pk')[:number]
    results = []
    for job in list_job:
        tests = []
        start_time = ""
        end_time = ''
        if job.start_time is not None:
            start_time = job.start_time.strftime('%Y-%m-%d %H:%M:%S')
        if job.end_time is not None:
            end_time = job.end_time.strftime('%Y-%m-%d %H:%M:%S')
        myjob = {'name': job.project, 'status': job.status, 'start': start_time,
                 'end': end_time, 'tests': tests}
        for test in job.job_test_set.all():
            tests.append(
                {'name': test.name, 'parameter': test.robot_parameter, 'status': test.status, 'log': test.test_log.id,
                 'id': test.id})
        if not tests:
            continue
        results.append(myjob)
    return HttpResponse(json.dumps(results), content_type='application/json')


def testproject_getall(request):
    list_project = Project.objects.all()
    return HttpResponse(serializers.serialize("json", list_project), content_type='application/json')


def testlab_getall(request):
    results = []
    list_project = Project.objects.all()
    for project in list_project:
        tests = []
        maps = Map.objects.filter(project=project.name, use=True)
        mylab = {'name': project.name, 'tests': tests}
        for map in maps:
            tests.append({'name': map.test, 'url': map.testurl, 'parameter': map.robot_parameter})
        results.append(mylab)
    return HttpResponse(json.dumps(results), content_type='application/json')


def testproject_testproject(request):
    tid = request.GET['tid']
    project = Project.objects.get(pk=tid)
    json = project.toJSON()
    return HttpResponse(json, content_type='application/json')


def scm_testproject(request):
    SCM = {'scms': [{'name': 'svn'}, {'name': 'git'}]}
    return HttpResponse(json.dumps(SCM), content_type='application/json')
