import pysvn
import git
import os
import env
import utility
import shutil
from pysvn._pysvn_2_7 import ClientError


class Manager(object):
    def __init__(self,job,project):
        self.job=job
        self.project = project
        self.scm = self.project.scm
        self.devpath = os.path.join(env.dev,self.project.name)
        
    def init(self):
        if self.scm == 'svn':
            client = pysvn.Client()
            if not os.path.exists(self.devpath):
                os.mkdir(self.devpath)
                utility.logmsg(self.job.log.path, 'checkout develop project,please waiting......')
                client.checkout(self.project.devurl,self.devpath)
                utility.logmsg(self.job.log.path, 'checkout develop project success')
            else:
                try:
                    client.info(self.devpath)
                    client.cleanup(self.devpath)
                    utility.logmsg(self.job.log.path, 'update develop project,please waiting......')
                    client.update(self.devpath)
                    utility.logmsg(self.job.log.path, 'update develop project success')
                except ClientError:
                    shutil.rmtree(self.devpath)
                    os.mkdir(self.devpath)
                    utility.logmsg(self.job.log.path, 'checkout develop project,please waiting......')
                    client.checkout(self.project.devurl,self.devpath)
                    utility.logmsg(self.job.log.path, 'checkout develop project success')
                except Exception,e:
                    utility.logmsg(self.job.log.path,e)
            entry = client.info(self.devpath)
            dev_revision_number = entry.commit_revision.number
            return dev_revision_number
        elif self.scm =='git':
            if not os.path.exists(self.devpath):
                utility.logmsg(self.job.log.path, 'checkout develop project,please waiting......')
                repo = git.Repo.clone_from(self.project.devurl,self.devpath,branch=self.project.branch)
                utility.logmsg(self.job.log.path, 'checkout develop project success')
            else:
                try:
                    g = git.Git(self.devpath)
                    g.clean('-xdf')
                    g.checkout(self.project.branch)
                    utility.logmsg(self.job.log.path, 'update develop project,please waiting......')
                    g.pull()
                    utility.logmsg(self.job.log.path, 'update develop project success')
                except git.exc.InvalidGitRepositoryError:
                    shutil.rmtree(self.devpath)
                    utility.logmsg(self.job.log.path, 'checkout develop project,please waiting......')
                    repo = git.Repo.clone_from(self.project.devurl,self.devpath,branch=self.project.branch)
                    utility.logmsg(self.job.log.path, 'checkout develop project success')
            repo = git.Repo(self.devpath)
            dev_revision_number = str(repo.head.commit)
            return dev_revision_number