import os
from  datetime import datetime

import pysvn

import env
import utility
from regression.models import Map, Job_Test, Test_Log

logdir = datetime.utcnow().strftime('%Y%m%d')


def test_automation_init(job):
    maps = Map.objects.filter(project=job.project, use=True)
    if len(maps) == 0:
        raise Exception("please config test automation for project(%s)" % job.project)
    for m in maps:
        job_test = Job_Test()
        job_test.job = job
        job_test.status = 'waiting'
        job_test.robot_parameter = m.robot_parameter
        job_test.testurl = m.testurl
        job_test.name = m.test
        job_test.report = "%s/%s_%s" % (
            datetime.utcnow().strftime('%Y%m%d'), datetime.utcnow().strftime('%H%M%S'), m.test)
        job_test.save()
        log = Test_Log()
        log.test = job_test
        log.path = "%s/%s.log" % (logdir, datetime.utcnow().strftime('%H%M%S'))
        log.save()


def test_svn_checkout(test):
    utility.logmsg(test.test_log.path, "checkout test automation from svn")
    testpath = os.path.join(env.test, test.name)
    client = pysvn.Client()
    if os.path.exists(testpath):
        utility.remove_file(testpath)
    os.mkdir(testpath)
    client.checkout(test.testurl, testpath)
    entry = client.info(testpath)
    test.revision_number = entry.commit_revision.number
    test.save()
