import pysvn
import os
import re
import env
from lxml import etree
import smtplib
from email.mime.text import MIMEText
import tenjin
tenjin.set_template_encoding("utf-8")
from tenjin.helpers import *
import sys

mswindows = (sys.platform == "win32")

def rendestring(string):
    if string !="":
        _variable_pattern = r'\$\{[^\}]+\}'
        match = re.findall(_variable_pattern,string)
        if match:
            for arg in match:
                string =  string.replace(arg,str(get_variable_value(arg)))
        return string

def matchre(path):
    warpath =  os.path.split(path)
    filelist  =os.listdir(warpath[0])
    for f in filelist:
        if warpath[-1] == f:
            return os.path.join(warpath[0],f)
        pattern= re.compile(warpath[-1].replace('$','\\'))
        match  = pattern.match(f)
        if match:
            return os.path.join(warpath[0],match.group())

def get_variable_value(arg):
    if env.variables.has_key(arg):
        return env.variables[arg]
    else:
        return arg

def mklogdir(dirpath):
    dirpath = os.path.join(env.log,dirpath)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)

def logmsgs(logpath,msgs):
    f = open(os.path.join(env.log,logpath),'a')
    f.writelines(msgs)
    f.write('\n')
    f.close()

def logmsg(logpath,msg):
    f = open(os.path.join(env.log,logpath),'a')
    f.write(msg)
    f.write('\n')
    f.close()


def get_result_fromxml(outputpath):
    tree = etree.parse(outputpath)
    root = tree.getroot()
    result = root.xpath('/robot/suite/status')
    status =  result[0].attrib['status']
    return status

def set_email(test,host):
    emailfile = env.email
    context = {
               "run_time":str(test.job.start_time),
#                "job_number":test.job.job_number,
               "project":test.job.project,
               'release_build':test.job.dev_revision_number,
               'test_version':test.revision_number,
               'result':test.status,
               'reportlink':'http://%s/regression/report/%s'%(host,test.id)}
    path = '\\'.join((emailfile.split('\\'))[:-1])
    engine = tenjin.Engine(path=[path],cache=tenjin.MemoryCacheStorage())
    emailstring =  engine.render(emailfile, context)
    return str(emailstring)


def send_email(test,host):
    receiver =  test.job.email
    if receiver != '':
        sender = "Daniel.liu@derbysoft.com"
    #     subject = '%s_%s_%s_%s_%s'%(test.status,test.job.job_number,test.job.dev_revision_number,test.revision_number,test.name)
        subject = '%s_Regression_Test_%s'%(test.job.project,test.status)
        smtpserver = 'mail.derbysoft.com:465'
        username = "Daniel.liu@derbysoft.com"
        password='Lf1988720'
        msg=MIMEText(set_email(test,host),'html')
        msg['Subject']= subject
        smtp= smtplib.SMTP_SSL(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver,msg.as_string())
        smtp.quit()
    
def update_Doraemon():
    if not mswindows:
        client = pysvn.Client()
        try:
            client.update(env.Doraemon)
        except Exception,e:
            print e

def delete_svn_unversioned(self,rootdir):
    client = pysvn.Client()
    for parent,dirnames,filenames in os.walk(rootdir):
        if parent.find('.svn') == -1:
            for dirname in  dirnames:
                if dirname.find('.svn') == -1 :
                    dirpath = os.path.join(parent,dirname)
                    entry = client.info(dirpath)         
                    if entry is None:
                        os.removedirs(dirpath)
                        print dirpath
                
            for filename in filenames:
                filepath = os.path.join(parent,filename)       
                entry = client.info(filepath)         
                if entry is None:
                    os.remove(filepath)
                    print filepath