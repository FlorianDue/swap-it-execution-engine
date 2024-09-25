import time, os, sys
#add directories to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), "../."))
sys.path.append(os.path.join(os.path.dirname(__file__), "../tests/test_helpers/."))
#import the main function
from main import main
#import the docker environment
from util.start_docker_compose import DockerComposeEnvironment

if __name__ == '__main__':
    #configure the required docker environment
    env = DockerComposeEnvironment(["Device_Registry", "Service_Server", "Dashboard"])
    #start the docker environment
    env.run_docker_compose("./Tutorial/docker-compose.yaml")
    #wait until the server started
    time.sleep(10)
    #run the execution engine
    main()
    #shut down the docker environment
    env.stop_docker_compose()