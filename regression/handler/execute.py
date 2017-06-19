import threading
from regression.models import Job, Project,build,Map,Job_Test
from regression.manager import Manager
import regression.env as env
import os
import utility
import subprocess
import pysvn
from datetime import *
import shutil
import json
import time
import sys
mswindows = (sys.platform == "win32")


class Execute(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.host = ""
        self.job = None

    def run(self):
        pass

    def starts(self):
        self.dev_init()
        self.dev_build()
        self.test_init()
        self.test_copy_war()
        self.do_job()

    def dev_init(self):
        project = Project.objects.get(pk=self.project)
        m = Manager(self, project)
        self.job.dev_revision_number = m.init()
        env.variables['${project_revision}'] = self.job.dev_revision_number
        self.save()

    def dev_build(self):
        bc = build.objects.filter(project=self.project)
        if len(bc) == 0:
            bc = build.objects.filter(project=env.top_build)
        self.job.build_command = bc[0].build_command
        self.job.save()
        buildpath = os.path.join(env.dev, self.project)
        opath = os.getcwd()
        utility.logmsgs(self.log.path, "cd %s" % buildpath)
        os.chdir(buildpath)
        utility.logmsg(self.log.path, self.build_command)
        bp = subprocess.Popen(self.build_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while True:
            log = bp.stdout.readline()
            try:
                log = log.encode("utf-8")
            except Exception:
                log = log.decode("gbk").encode("utf-8")
            utility.logmsg(self.log.path, log.replace('\r\n', ''))
            if bp.poll() is not None:
                break
        os.chdir(opath)

    def test_init(self):
        client = pysvn.Client()
        maps = Map.objects.filter(project=self.project, use=True)
        if len(maps) == 0:
            raise Exception("please config test mpas for project(%s)" % self.project)
        for m in maps:
            testpath = os.path.join(env.test, m.test)
            if os.path.exists(testpath):
                shutil.rmtree(testpath)
            os.mkdir(testpath)
            client.checkout(m.testurl, testpath)
            entry = client.info(testpath)
            job_test = Job_Test()
            job_test.job = self
            job_test.status = 'w'
            job_test.robot_parameter = m.robot_parameter
            job_test.name = m.test
            job_test.revision_number = entry.commit_revision.number
            job_test.report = "%s/%s_%s" % (
                datetime.utcnow().strftime('%Y%m%d'), datetime.utcnow().strftime('%H%M%S'), m.test)
            job_test.save()

    def test_copy_war(self):
        devpath = os.path.join(env.dev, self.project)
        maps = Map.objects.filter(project=self.project, use=True)
        for m in maps:
            apppath = os.path.join(env.test, m.test, env.app)
            if m.war != "":
                wars = utility.rendestring(m.war)
                wars = wars.split(',')
                for war in wars:
                    ws = war.split(':')
                    srcpath = utility.matchre(os.path.join(devpath, ws[0]))
                    #                     srcpath = os.path.join(devpath,ws[0])
                    targetpath = os.path.join(apppath, ws[-1])
                    if os.path.exists(srcpath):
                        if ws[-1].find('.war') > -1:
                            utility.logmsg(self.log.path, 'copy %s to %s' % (srcpath, targetpath))
                            shutil.copyfile(srcpath, targetpath)
                        else:
                            if os.path.exists(targetpath):
                                shutil.rmtree(targetpath)
                            command = "unzip -ao '%s' -d '%s' " % (srcpath, targetpath)
                            utility.logmsg(self.log.path, command)
                            unzip = subprocess.Popen(command, shell=True)
                    else:
                        raise Exception("can't find this war(%s)" % srcpath)

    def do_job(self):
        preid = int(self.id) - 1
        while True:
            try:
                prejob = Job.objects.get(pk=preid)
                if prejob.status == 'd' or prejob.status == 'e':
                    break
            except Exception:
                break
            time.sleep(5)
        self.status = 'r'
        self.save()
        job_tests = self.job_test_set.all()
        for test in job_tests:
            try:
                self.execute(test)
            except Exception, e:
                utility.logmsg(self.log.path, e)
        self.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.save()

    def get_results(self):
        global ip
        jtests = self.job_test_set.all()
        status = True
        result = {}
        tests = []
        for t in jtests:
            testdict = {}
            status = t.status
            testdict['name'] = t.name
            testdict['status'] = t.status
            testdict['report'] = "http://%s/regression/report/%s" % (ip, t.id)
            tests.append(testdict)
            if status == 'FAIL':
                status = False
        if status:
            result['result'] = 'PASS'
        else:
            result['result'] = 'FAIL'
        result['tests'] = tests
        return json.dumps(result, encoding='utf-8')

    def save_log(self):
        f = open(os.path.join(env.log, self.log.path), 'r')
        fstr = f.read()
        f.close()
        self.log.text = fstr
        self.log.save()

    def execute(self, test):
        utility.update_Doraemon()
        global ip
        test.status = 'r'
        testpath = os.path.join(env.test, test.name)
        reportpath = os.path.join(env.report, test.report)
        test.save()
        robot = None
        opath = os.getcwd()
        os.chdir(testpath)
        if mswindows:
            command = "pybot.bat  %s --outputdir %s  %s" % (test.robot_parameter, reportpath, testpath)
            utility.logmsg(self.log.path, command)
            #             print command
            robot = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            command = "pybot  %s --outputdir %s  %s" % (test.robot_parameter, reportpath, testpath)
            utility.logmsg(self.log.path, command)
            #             print command
            robot = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        test.pid = robot.pid
        test.save()
        while True:
            log = robot.stdout.readline()
            try:
                log = log.encode("utf-8")
            except Exception:
                log = log.decode("gbk").encode("utf-8")
            utility.logmsgs(self.log.path, log.replace('\r\n', ''))
            if robot.poll() is not None:
                break
        test.status = utility.get_result_fromxml(os.path.join(reportpath, env.output_xml))
        test.save()
        try:
            utility.send_email(test, ip)
            utility.logmsgs(self.log.path, 'send email success')
        except Exception, e:
            utility.logmsgs(self.log.path, 'send email error:%s', str(e))
        os.chdir(opath)
