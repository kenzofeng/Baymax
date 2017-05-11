from ..models import Project,Map,build
import json

def Project_toJson(project):
    mlist=[]
    maps = Map.objects.filter(project=project.name)
    for m in maps:
        mdatas={'pk':m.pk,'test':m.test,'url':m.testurl,'robot':m.robot_parameter,'war':m.war}
        mlist.append(mdatas)
    mb=build.objects.filter(project=project.name)
    if len(mb)>0:
        build_command = mb[0].build_command
    else:
        build_command=''
    data={'pk':project.name,'name':project.name,'scm':project.scm,'url':project.devurl,'branch':project.branch,'email':project.email,'build':build_command,'maps':mlist}
    return json.dumps(data)