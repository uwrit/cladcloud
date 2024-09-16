On a new action runner:
install linux
install docker

Not only do we need to follow the instructions to install the runner:
https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service

But also set/enable SELinux contexts:
https://github.com/actions/runner/issues/410

