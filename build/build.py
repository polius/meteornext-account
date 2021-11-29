import os
import time
import json
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
        self.__show_header()
        print("|           Build            |")
        print("+============================+")
        self.clean()
        os.makedirs('{}/dist'.format(self._pwd), exist_ok=True)
        subprocess.call("cd {}/client ; npm run build".format(self._pwd), shell=True)
        subprocess.call("mv {0}/client/dist {0}/dist/client".format(self._pwd), shell=True)
        subprocess.call("cd {}/dist/ ; tar -czvf client.tar.gz client ; rm -rf client".format(self._pwd), shell=True)
        subprocess.call("docker pull nginx:alpine", shell=True)
        subprocess.call("cd {} ; docker build -t meteor2-account:latest -f build/Dockerfile .".format(self._pwd), shell=True)
        subprocess.call("docker rmi nginx:alpine", shell=True)
        subprocess.call("docker save meteor2-account | gzip > {}/dist/meteor2-account.tar.gz".format(self._pwd), shell=True)
        subprocess.call("rm -rf {}/dist/client.tar.gz".format(self._pwd), shell=True)
        self.start()

    def start(self):
        with open(f"{self._pwd}/server/server.conf") as fopen:
            conf = json.load(fopen)
        # Build environment variables
        environment = ''
        environment += f" -e SQL_ENGINE='{conf['sql']['engine']}'"
        environment += f" -e SQL_HOST='{conf['sql']['hostname']}'"
        environment += f" -e SQL_PORT='{conf['sql']['port']}'"
        environment += f" -e SQL_USER='{conf['sql']['username']}'"
        environment += f" -e SQL_PASS='{conf['sql']['password']}'"
        environment += f" -e SQL_DB='{conf['sql']['database']}'"
        environment += f" -e AWS_REGION_NAME='{conf['aws']['region_name']}'"
        environment += f" -e AWS_ACCESS_KEY='{conf['aws']['access_key']}'"
        environment += f" -e AWS_SECRET_ACCESS_KEY='{conf['aws']['secret_access_key']}'"
        environment += f" -e STRIPE_API_KEY='{conf['stripe']['api_key']}'"
        environment += f" -e STRIPE_WEBHOOK_SECRET='{conf['stripe']['webhook_secret']}'"
        environment += f" -e HCAPTCHA_SECRET='{conf['hcaptcha']['secret']}'"
        print("- Importing image...")
        subprocess.call("docker load -i {}/dist/meteor2-account.tar.gz".format(self._pwd), shell=True)
        subprocess.call("rm -rf {}/dist/meteor2-account.tar.gz".format(self._pwd), shell=True)
        print("- Starting new container...")
        container_id = subprocess.check_output("docker run --name meteor2-account -itd -p12351:80{} meteor2-account".format(environment), shell=True)
        print("- Container ID: {}".format(container_id.decode("utf-8")[:12]))
        print("- Overall Time: {}".format(time.strftime('%H:%M:%S', time.gmtime(time.time()-self._start_time))))

    def clean(self):
        subprocess.call("rm -rf {}/dist/meteor2-account.tar.gz".format(self._pwd), shell=True)
        subprocess.call("rm -rf {}/dist/client.tar.gz".format(self._pwd), shell=True)
        subprocess.call("docker kill $(docker ps -a -q --filter ancestor='meteor2-account') >/dev/null 2>&1", shell=True)
        subprocess.call("docker rm $(docker ps -a -q --filter ancestor='meteor2-account') >/dev/null 2>&1", shell=True)
        subprocess.call("docker rmi meteor2-account:latest >/dev/null 2>&1", shell=True)

    ####################
    # Internal Methods #
    ####################
    def __show_header(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("+============================+")
        print("|    Meteor Next - Account   |")
        print("+============================+")