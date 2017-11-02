import os
import re
import smtplib
from email.mime.text import MIMEText

import pysvn
import tenjin
from lxml import etree

import env

tenjin.set_template_encoding("utf-8")
from tenjin.helpers import *
import sys
import subprocess

mswindows = (sys.platform == "win32")


def rendestring(string):
    if string != "":
        _variable_pattern = r'\$\{[^\}]+\}'
        match = re.findall(_variable_pattern, string)
        if match:
            for arg in match:
                string = string.replace(arg, str(get_variable_value(arg)))
        return string


def matchre(path):
    warpath = os.path.split(path)
    filelist = os.listdir(warpath[0])
    for f in filelist:
        if warpath[-1] == f:
            return os.path.join(warpath[0], f)
        pattern = re.compile(warpath[-1].replace('$', '\\'))
        match = pattern.match(f)
        if match:
            return os.path.join(warpath[0], match.group())


def get_variable_value(arg):
    if env.variables.has_key(arg):
        return env.variables[arg]
    else:
        return arg


def mklogdir(dirpath):
    dirpath = os.path.join(env.log, dirpath)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def logmsgs(logpath, msgs):
    f = open(os.path.join(env.log, logpath), 'a')
    f.writelines(msgs)
    f.write('\n')
    f.close()


def logmsg(logpath, msg):
    f = open(os.path.join(env.log, logpath), 'a')
    f.write(msg)
    f.write('\n')
    f.close()


def get_result_fromxml(outputpath):
    tree = etree.parse(outputpath)
    root = tree.getroot()
    result = root.xpath('/robot/suite/status')
    status = result[0].attrib['status']
    return status


def remove_file(fpath):
    if mswindows:
        os.system('rd /S/Q %s' % fpath)
    else:
        os.system('rm -rf %s' % fpath)


def save_test_log(test):
    log_path = os.path.join(env.log, test.test_log.path)
    f = open(log_path, 'r')
    fstr = f.read()
    f.close()
    test.test_log.text = fstr
    test.test_log.save()


def save_log(job):
    log_path = os.path.join(env.log, job.log.path)
    f = open(log_path, 'r')
    fstr = f.read()
    f.close()
    job.log.text = fstr
    job.log.save()


def set_email(test, host):
    emailfile = env.email
    context = {
        "run_time": str(test.job.start_time),
        #                "job_number":test.job.job_number,
        "project": test.job.project,
        'log': 'http://%s/regression/test/log/%s' % (host, test.test_log.id),
        'test_version': test.revision_number,
        'result': test.status,
        'reportlink': 'http://%s/regression/report/%s' % (host, test.id)}
    path = '\\'.join((emailfile.split('\\'))[:-1])
    engine = tenjin.Engine(path=[path], cache=tenjin.MemoryCacheStorage())
    emailstring = engine.render(emailfile, context)
    return str(emailstring)


def send_email(test, host):
    receiver = test.job.email
    if receiver != '':
        sender = "Daniel.liu@derbysoft.com"
        #     subject = '%s_%s_%s_%s_%s'%(test.status,test.job.job_number,test.job.dev_revision_number,test.revision_number,test.name)
        subject = '%s_Regression_Test_%s' % (test.job.project, test.status)
        smtpserver = 'mail.derbysoft.com:465'
        username = "Daniel.liu@derbysoft.com"
        password = 'Lf1988720'
        msg = MIMEText(set_email(test, host), 'html')
        msg['Subject'] = subject
        smtp = smtplib.SMTP_SSL(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()


def update_Doraemon():
    if not mswindows:
        client = pysvn.Client()
        try:
            client.update(env.Doraemon)
        except Exception, e:
            print e


def run_autobuild(test):
    test_app_autobuid = os.path.join(env.test, test.name, 'app', 'autobuild.py')
    test_app_autobuild_autobuid = os.path.join(env.test, test.name, 'app', 'autobuild', 'autobuild.py')
    autobuild = None
    if os.path.exists(test_app_autobuid):
        command = "python %s run" % (test_app_autobuid)
        logmsg(test.test_log.path, command)
        autobuild = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    elif os.path.exists(test_app_autobuild_autobuid):
        command = "python %s run" % (test_app_autobuild_autobuid)
        logmsg(test.test_log.path, command)
        autobuild = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    else:
        logmsg(test.test_log.path, "not found autobuild.py to build your app")
        return True
    while True:
        log = autobuild.stdout.readline()
        logmsgs(test.test_log.path, log.replace('\r\n', ''))
        if 'ERROR' in log:
            return False
        if autobuild.poll() is not None:
            return True


def delete_svn_unversioned(self, rootdir):
    client = pysvn.Client()
    for parent, dirnames, filenames in os.walk(rootdir):
        if parent.find('.svn') == -1:
            for dirname in dirnames:
                if dirname.find('.svn') == -1:
                    dirpath = os.path.join(parent, dirname)
                    entry = client.info(dirpath)
                    if entry is None:
                        os.removedirs(dirpath)
                        print dirpath

            for filename in filenames:
                filepath = os.path.join(parent, filename)
                entry = client.info(filepath)
                if entry is None:
                    os.remove(filepath)
                    print filepath
