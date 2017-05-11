# -*- coding: utf-8 -*- 
from django.db import models
import pysvn
import env
import os
import subprocess
import shutil
import sys
import utility
from datetime import *
import time
import json
from manager import Manager

ip=''

mswindows = (sys.platform == "win32")

class Svn(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
    password = models.CharField(max_length=50)
    
SCM=(
     ('svn','svn'),
     ('git','git'),
     )

class Project(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
    scm = models.CharField(max_length=10,choices=SCM)
    branch=models.CharField(max_length=250)
    devurl = models.CharField(max_length=250)
    email=models.CharField(max_length=250)
    
    def toJSON(self):
        mlist=[]
        maps = Map.objects.filter(project=self.name)
        for m in maps:
            mdatas={'pk':m.pk,'test':m.test,'url':m.testurl,'robot':m.robot_parameter,'war':m.war}
            mlist.append(mdatas)
        mb=build.objects.filter(project=self.name)
        if len(mb)>0:
            build_command = mb[0].build_command
        else:
            build_command=''
        data={'pk':self.name,'name':self.name,'scm':self.scm,'url':self.devurl,'branch':self.branch,'email':self.email,'build':build_command,'maps':mlist}
        return json.dumps(data)
    
    
class Map(models.Model):
    project = models.CharField(max_length=50)
    test = models.CharField(max_length=50)
    testurl = models.CharField(max_length=250)
    robot_parameter = models.CharField(max_length=250,blank=True,null=True,default='')
    war = models.TextField(blank=True,null=True)
    use = models.BooleanField(default=True)
    
    def touse(self):
        if self.use:
            return 'yes'
        else:
            return 'no'
    
Run_Status=(
             ('r','running'),
             ('d','done'),
             ('e','error'),
             ('w','waiting'),
             ('FAIL','FAIL'),
             ('PASS','PASS'),
             )
    
class Job(models.Model):
    project = models.CharField(max_length=50)
    status = models.CharField(max_length=20,choices=Run_Status)
    start_time = models.DateTimeField(blank=True,null=True)
    end_time = models.DateTimeField(blank=True,null=True)
    build_command = models.CharField(max_length=250,blank=True,null=True)
    job_number = models.CharField(max_length=20,blank=True,null=True)
    dev_revision_number = models.CharField(max_length=250,blank=True,null=True)
    email = models.CharField(max_length=100,blank=True,null=True)
    
    def __str__(self):
        return self.project
    
    
    def starts(self,host):
        global ip
        ip=host
        self.dev_init()
        self.dev_build()
        self.test_init()
        self.test_copy_war()    
        self.do_job()
    
    def dev_init(self):
        project = Project.objects.get(pk=self.project)
        m = Manager(self,project)
        self.dev_revision_number = m.init()
        env.variables['${project_revision}'] = self.dev_revision_number
        self.save()
    
    def dev_build(self):
        bc = build.objects.filter(project=self.project)
        if len(bc) == 0:
            bc = build.objects.filter(project=env.top_build)
        self.build_command = bc[0].build_command
        self.save()
        buildpath = os.path.join(env.dev,self.project)
        opath = os.getcwd()
        utility.logmsgs(self.log.path,"cd %s"%buildpath)
        os.chdir(buildpath)
        utility.logmsg(self.log.path,self.build_command)
        bp = subprocess.Popen(self.build_command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        while True:
            log = bp.stdout.readline()
            try:
                log =log.encode("utf-8")
            except Exception:
                log =log.decode("gbk").encode("utf-8")
            utility.logmsg(self.log.path, log.replace('\r\n', ''))
#             print log.replace('\r\n', '').decode('gbk').encode("utf-8")
            if bp.poll() is not None:
                break
        os.chdir(opath)
    
    def test_init(self):
        client = pysvn.Client()
        maps = Map.objects.filter(project=self.project,use=True)
        if len(maps) == 0:
            raise Exception,"please config test mpas for project(%s)"%self.project
        for m in  maps:
            testpath = os.path.join(env.test,m.test)
            if os.path.exists(testpath):
                shutil.rmtree(testpath)
            os.mkdir(testpath)
            client.checkout(m.testurl,testpath)
            entry = client.info(testpath)
            job_test= Job_Test()
            job_test.job = self
            job_test.status = 'w'
            job_test.robot_parameter = m.robot_parameter
            job_test.name = m.test
            job_test.revision_number = entry.commit_revision.number
            job_test.report= "%s/%s_%s"%(datetime.utcnow().strftime('%Y%m%d'),datetime.utcnow().strftime('%H%M%S'),m.test)
            job_test.save()
            
    def test_copy_war(self):
        devpath =  os.path.join(env.dev,self.project)
        maps = Map.objects.filter(project=self.project,use=True)
        for m in  maps:
            apppath  = os.path.join(env.test,m.test,env.app)
            if m.war != "":
                wars = utility.rendestring(m.war)
                wars = wars.split(',')
                for war in wars:
                    ws = war.split(':')
                    srcpath = utility.matchre(os.path.join(devpath,ws[0]))
#                     srcpath = os.path.join(devpath,ws[0])
                    targetpath = os.path.join(apppath,ws[-1])
                    if os.path.exists(srcpath):
                        if ws[-1].find('.war') > -1:
                            utility.logmsg(self.log.path,'copy %s to %s'%(srcpath,targetpath))
                            shutil.copyfile(srcpath,targetpath)
                        else:
                            if os.path.exists(targetpath):
                                shutil.rmtree(targetpath)
                            command="unzip -ao '%s' -d '%s' "%(srcpath,targetpath)
                            utility.logmsg(self.log.path, command)
                            unzip = subprocess.Popen(command,shell=True)
                    else:
                        raise Exception,"can't find this war(%s)"%srcpath
    
    def do_job(self):
        preid = int(self.id)-1
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
        job_tests= self.job_test_set.all()
        for test in job_tests:
            try:
                self.execute(test)
            except Exception,e:
                utility.logmsg(self.log.path, e)
        self.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.save()
    
    
    def get_results(self):
        global ip
        jtests = self.job_test_set.all()
        status = True
        result={}
        tests = []
        for t in jtests:
            testdict= {}
            status = t.status
            testdict['name']= t.name
            testdict['status']= t.status
            testdict['report']= "http://%s/regression/report/%s"%(ip,t.id)
            tests.append(testdict)
            if status =='FAIL':
                status = False
        if status:
            result['result'] = 'PASS'
        else:
            result['result'] = 'FAIL'
        result['tests']=tests
        return json.dumps(result,encoding='utf-8')
        
    def save_log(self):
        f= open(os.path.join(env.log,self.log.path),'r')
        fstr  =f.read()
        f.close()
        self.log.text = fstr
        self.log.save()
    
    
    def execute(self,test):
        utility.update_Doraemon()
        global ip
        test.status = 'r'
        testpath = os.path.join(env.test,test.name)
        reportpath = os.path.join(env.report,test.report)
        test.save()
        robot = None
        opath = os.getcwd()
        os.chdir(testpath)
        if mswindows:
            command = "pybot.bat  %s --outputdir %s  %s"%(test.robot_parameter,reportpath,testpath)
            utility.logmsg(self.log.path, command)
#             print command
            robot = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        else:
            command = "pybot  %s --outputdir %s  %s"%(test.robot_parameter,reportpath,testpath)
            utility.logmsg(self.log.path, command)
#             print command
            robot = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        test.pid = robot.pid
        test.save()
        while True:
            log = robot.stdout.readline()
            try:
                log =log.encode("utf-8")
            except Exception:
                log =log.decode("gbk").encode("utf-8")
            utility.logmsgs(self.log.path, log.replace('\r\n', ''))
            if robot.poll() is not None:
                break
        test.status = utility.get_result_fromxml(os.path.join(reportpath,env.output_xml))
        test.save()
        try:
            utility.send_email(test,ip)
            utility.logmsgs(self.log.path,'send email success')
        except Exception,e:
            utility.logmsgs(self.log.path, 'send email error:%s',str(e))
        os.chdir(opath)
                    
class Job_Test(models.Model):
    job = models.ForeignKey(Job)
    robot_parameter = models.CharField(max_length=250,blank=True,null=True,default='')
    name = models.CharField(max_length=50,blank=True,null=True,default='')
    pid = models.CharField(max_length=50,blank=True,null=True,default='')
    status = models.CharField(max_length=20,choices=Run_Status,blank=True,null=True,)
    revision_number = models.CharField(max_length=50,blank=True,null=True,)
    report= models.CharField(max_length=250,blank=True,null=True,)
    

class Log(models.Model):
    job = models.OneToOneField(Job)
    path = models.CharField(max_length=250)
    text =  models.TextField(blank=True,null=True)

class build(models.Model):
    project =  models.CharField(max_length=50)
    build_command =  models.TextField(blank=True,null=True)
    
    