import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

Jenkins_rul = 'http://localhost:8080/jenkins/'
# Jenkins_rul='http://jenkins.derbysoft.tm/jenkins/'
Doraemon = r'/usr/local/lib/python2.7/site-packages/Doraemon'

opath = os.getcwd()
project = 'project'
app = 'app'
dev = os.path.join(BASE_DIR, project, 'dev')
test = os.path.join(BASE_DIR, project, 'test')
report = os.path.join(BASE_DIR, project, 'report')
log = os.path.join(BASE_DIR, project, 'log')
top_build = 'top_build'

log_html = 'log.html'
report_html = 'report.html'
output_xml = 'output.xml'
deps = 'deps'
email = os.path.join(BASE_DIR, project, 'email.xml')

receiver = 'daniel.liu@derbysoft.com'

variables = {'${project_revision}': ""}
