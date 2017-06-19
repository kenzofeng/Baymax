from regression.models import Job, Project, Log
from datetime import *
import regression.utility as utility
from django.core.exceptions import ObjectDoesNotExist

logdir = datetime.utcnow().strftime('%Y%m%d')


def start(request, project):
    try:
        p = Project.objects.get(pk=project)
        utility.mklogdir(logdir)
        job = Job(project=project, status='w', start_time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                  job_number="", email=p.email)
        job.save()
        log = Log()
        log.job = job
        log.path = "%s/%s.log" % (logdir, datetime.utcnow().strftime('%H%M%S'))
        log.save()
        return job.id
    except ObjectDoesNotExist:
        raise Exception("%s doesn't exist,please config in Baymax System!" % (project))
    except Exception, e:
        job.end_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        job.status = 'e'
        job.save()
        utility.logmsg(job.log.path, str(e))
        job.save_log()
        raise Exception(e)
