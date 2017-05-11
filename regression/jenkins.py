from jenkinsapi.jenkins import Jenkins
from lxml import etree
import env

email="./reporters//recipients"

class JenkinsProject(object):
    def __init__(self,name):
        self.name=''
        self.url=''
        self.scm=''
        self.buildnumber=''
        self.email=''
    
        
def get_dev(project):
    server = Jenkins(env.Jenkins_rul)
    for j in server.get_jobs():
        if j[0] == project:
            job_instance = server.get_job(j[0])
            jp = JenkinsProject(project)
            jp.url = job_instance.get_scm_url()[0]
            jp.scm = job_instance.get_scm_type()
            jp.buildnumber = job_instance.get_last_buildnumber()
            root = etree.XML(str(job_instance._config).encode("utf-8"))
            if len(root.findall(email)) > 0:
                jp.email = root.findall(email)[0].text
            return jp
    raise Exception,"can't find project(%s) from jenkins"%(project)
