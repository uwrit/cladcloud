On a new action runner:
- install linux
- install docker

Add docker group and add the user to it:
https://access.redhat.com/solutions/7001773
```
group add docker
usermod -aG docker github
systemctl --user enable --now dbus
loginctl enable-linger 1000
```

Not only do we need to follow the instructions to install the runner:
https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service

Alternatively:
https://github.com/vbem/multi-runners

But also set/enable SELinux contexts:
https://github.com/actions/runner/issues/410

