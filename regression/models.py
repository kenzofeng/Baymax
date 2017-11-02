# -*- coding: utf-8 -*- 
import json
import sys

from django.db import models

mswindows = (sys.platform == "win32")


class Svn(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=50)


class Project(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    email = models.CharField(max_length=250)

    def toJSON(self):
        mlist = []
        maps = Map.objects.filter(project=self.name)
        for m in maps:
            mdatas = {'pk': m.pk, 'test': m.test, 'url': m.testurl, 'robot': m.robot_parameter}
            mlist.append(mdatas)
        data = {'pk': self.name, 'name': self.name, 'email': self.email, 'maps': mlist}
        return json.dumps(data)


class FTP(models.Model):
    ip = models.CharField(max_length=50)


class ProjectFTP(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ftp = models.ForeignKey(FTP, on_delete=models.SET_NULL, null=True)
    path = models.CharField(max_length=500)


class Map(models.Model):
    project = models.CharField(max_length=50)
    test = models.CharField(max_length=50)
    testurl = models.CharField(max_length=250)
    robot_parameter = models.CharField(max_length=250, blank=True, null=True, default='')
    use = models.BooleanField(default=True)

    def touse(self):
        if self.use:
            return 'yes'
        else:
            return 'no'


Run_Status = (
    ('running', 'running'),
    ('done', 'done'),
    ('error', 'error'),
    ('waiting', 'waiting'),
    ('FAIL', 'FAIL'),
    ('PASS', 'PASS'),
)


class Job(models.Model):
    project = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Run_Status)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    build_command = models.CharField(max_length=250, blank=True, null=True)
    job_number = models.CharField(max_length=20, blank=True, null=True)
    dev_revision_number = models.CharField(max_length=250, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.project


class Job_Test(models.Model):
    job = models.ForeignKey(Job)
    testurl = models.CharField(max_length=250)
    robot_parameter = models.CharField(max_length=250, blank=True, null=True, default='')
    name = models.CharField(max_length=50, blank=True, null=True, default='')
    pid = models.CharField(max_length=50, blank=True, null=True, default='')
    status = models.CharField(max_length=20, choices=Run_Status, blank=True, null=True, )
    revision_number = models.CharField(max_length=50, blank=True, null=True, )
    report = models.CharField(max_length=250, blank=True, null=True, )


class Test_Log(models.Model):
    test = models.OneToOneField(Job_Test)
    path = models.CharField(max_length=250)
    text = models.TextField(blank=True, null=True)


class Log(models.Model):
    job = models.OneToOneField(Job)
    path = models.CharField(max_length=250)
    text = models.TextField(blank=True, null=True)
