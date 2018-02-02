# Example curl request for new project: curl --data 'name=new_project&slug=project_slug' -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/teams/sentry/matt-tung-test/projects/
# Example curl request for project client keys/DSN: curl -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/projects/sentry/test2/keys/
# Example curl request for deleting existing project: curl -X "DELETE" -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/projects/sentry/new_project/
# Example curl request for retrieving project: curl -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/projects/sentry/test2/

import requests
import os


#s = requests.Session()
#s.auth = ('mtung@mit.edu', 'Charizard27!')
#q = s.get('https://brkpad.vivint.com/api/0/projects/sentry/test2/', headers={'Authorization': 'Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40'})
#print(q)

#project = os.popen("curl -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/projects/sentry/test69/").read()
#print(project)


def project(name):
        project = os.popen("curl -H 'Authorization: Bearer d60b195d9c0449f8bbc8bf612683376024ca6b3ed3984cb4898801c51ba97d40' https://brkpad.vivint.com/api/0/projects/sentry/"+name+"/").read()
        if len(project) == 1:
                pass
                #make project
                #get DSN
        return #make project


print(check_project('test2'))
