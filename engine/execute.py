import os
import subprocess
import sys
import time
from datetime import datetime

import env
import ts
import utility
from regression.models import Job

mswindows = (sys.platform == "win32")


class Execute():
    def __init__(self, job, ip):
        self.ip = ip
        self.job = job

    def run(self):
        ts.test_automation_init(self.job)
        self.do_job()

    def do_job(self):
        preid = int(self.job.id) - 1
        while True:
            try:
                prejob = Job.objects.get(pk=preid)
                if prejob.status == 'done' or prejob.status == 'error':
                    break
            except Exception:
                break
            time.sleep(2)
        self.job.status = 'running'
        self.job.save()
        job_tests = self.job.job_test_set.all()
        for test in job_tests:
            self.execute(test)
        self.job.status = 'done'
        self.job.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.job.save()

    def execute(self, test):
        try:
            robot = None
            opath = os.getcwd()
            test.status = 'running'
            test.save()
            ts.test_svn_checkout(test)
            utility.update_Doraemon()
            if utility.run_autobuild(test):
                testpath = os.path.join(env.test, test.name)
                reportpath = os.path.join(env.report, test.report)
                os.chdir(testpath)
                if mswindows:
                    command = "pybot.bat  %s --outputdir %s  %s" % (test.robot_parameter, reportpath, testpath)
                    utility.logmsg(test.test_log.path, command)
                    robot = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                else:
                    command = "pybot  %s --outputdir %s  %s" % (test.robot_parameter, reportpath, testpath)
                    utility.logmsg(test.test_log.path, command)
                    robot = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
                test.pid = robot.pid
                test.save()
                while True:
                    log = robot.stdout.readline()
                    utility.logmsgs(test.test_log.path, log.replace('\r\n', ''))
                    if 'Report:' in log and 'report.html' in log:
                        break
                    if robot.poll() is not None:
                        break
                test.status = utility.get_result_fromxml(os.path.join(reportpath, env.output_xml))
                test.save()
            else:
                test.status = 'error'
                test.save()
            utility.send_email(test, self.ip)
        except Exception, e:
            test.status = 'error'
            test.save()
            utility.send_email(test, self.ip)
            utility.logmsg(test.test_log.path, e)
        finally:
            utility.save_test_log(test)
            if robot is not None:
                robot.terminate()
                robot.kill()
            os.chdir(opath)
