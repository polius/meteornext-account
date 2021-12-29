import os
import time
import subprocess

if __name__ == '__main__':
    from build import build
    build()

class build:
    def __init__(self):
        self._pwd = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/..')
        self._start_time = time.time()
        self.build()

    def build(self):
        print("+============================+")
        print("|    Meteor Next - Account   |")
        print("+============================+")
        subprocess.call(f"rm -rf {self._pwd}/dist/client.tar.gz", shell=True)
        os.makedirs('{}/dist'.format(self._pwd), exist_ok=True)
        subprocess.call("cd {}/client ; npm run build".format(self._pwd), shell=True)
        subprocess.call("mv {0}/client/dist {0}/dist/client".format(self._pwd), shell=True)
        subprocess.call("cd {}/dist/ ; tar -czvf client.tar.gz client ; rm -rf client".format(self._pwd), shell=True)
        subprocess.call("docker pull nginx:alpine", shell=True)
        # One Time: create a new builder instance to be able to build for multiplatform
        # docker buildx create --use
        # subprocess.call(f"cd {self._pwd} ; docker buildx build -t meteor2-account:latest -f build/Dockerfile --no-cache --platform linux/amd64,linux/arm64 --load .", shell=True)
        subprocess.call(f"cd {self._pwd} ; docker buildx build -t meteor2-account:latest -f build/Dockerfile --no-cache --platform linux/arm64 --load .", shell=True)
        subprocess.call("docker rmi nginx:alpine", shell=True)
        subprocess.call(f"rm -rf {self._pwd}/dist/client.tar.gz", shell=True)
        subprocess.call("aws --profile meteor2-account ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 633757032102.dkr.ecr.eu-west-1.amazonaws.com", shell=True)
        subprocess.call("docker tag meteor2-account:latest 633757032102.dkr.ecr.eu-west-1.amazonaws.com/meteor2-account:latest", shell=True)
        subprocess.call("docker push 633757032102.dkr.ecr.eu-west-1.amazonaws.com/meteor2-account:latest", shell=True)
        subprocess.call("aws --profile meteor2-account ecs update-service --cluster meteor2 --service meteor2-account --force-new-deployment --region eu-west-1 --deployment-configuration minimumHealthyPercent=100,maximumPercent=200", shell=True)
        subprocess.call("docker rmi $(docker images 'meteor2-account' -a -q)", shell=True)
        # One-Time: Create new ecs task definition version with platform=arm64
        # aws --profile meteor2-account --region eu-west-1 ecs register-task-definition --cli-input-json file://ecs_task_definition.json
