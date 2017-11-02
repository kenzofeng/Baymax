import json
from datetime import *

from django.core.exceptions import ObjectDoesNotExist

import utility
from  execute import Execute
from regression.models import Job, Project, Log

logdir = datetime.utcnow().strftime('%Y%m%d')


def start(request, project):
    try:
        p = Project.objects.get(pk=project)
        utility.mklogdir(logdir)
        job = Job(project=project, status='waiting', start_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                  job_number="", email=p.email)
        job.save()
        log = Log()
        log.job = job
        log.path = "%s/%s.log" % (logdir, datetime.utcnow().strftime('%H%M%S'))
        log.save()
        utility.logmsg(log.path, "")
        execute = Execute(job, request.get_host())
        execute.run()
        utility.save_log(job)
        return get_results(request, job)
    except ObjectDoesNotExist:
        raise Exception("%s doesn't exist,please config in Baymax System!" % (project))
    except Exception, e:
        job.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        job.status = 'error'
        job.save()
        utility.logmsg(job.log.path, str(e))
        utility.save_log(job)
        raise Exception(e)

def get_results(request, job):
    jtests = job.job_test_set.all()
    status = True
    result = {}
    tests = []
    for t in jtests:
        testdict = {}
        status = t.status
        testdict['name'] = t.name
        testdict['status'] = t.status
        testdict['report'] = "http://%s/regression/report/%s" % (request.get_host(), t.id)
        testdict['runtime_log'] = "http://%s/regression/test/log/%s" % (request.get_host(), t.test_log.id)
        tests.append(testdict)
        if status == 'FAIL':
            status = False
    if status:
        result['result'] = 'PASS'
    else:
        result['result'] = 'FAIL'
    # result['log'] = "http://%s/regression/log/%s" % (request.get_host(), job.id)
    result['tests'] = tests
    return json.dumps(result, encoding='utf-8')
