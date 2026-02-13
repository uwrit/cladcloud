On a new action runner:
- install linux
- install actual docker (not podman which is default on RHEL) https://medium.com/@blackhorseya/switching-from-podman-to-docker-on-rhel-9-bd5e91f9f577

Add docker group and add the user to it:
https://access.redhat.com/solutions/7001773
```
group add docker
usermod -aG docker github
systemctl --user enable --now dbus
loginctl enable-linger 1000
```

Redirect /tmp on root volume to /home/tmp on large data volume:
```
mkdir /home/tmp
echo "/home/tmp	/tmp	none	defaults,bind	1 2" >> /etc/fstab
rm -rf /tmp/*
reboot
```

And redirect docker from /var/lib/docker to /home/docker:
```
service docker stop
cd /var/lib
mv docker /home/docker
ln -s /home/docker .
sed -i 's|dockerd|dockerd --data-root /home/docker|g' /lib/systemd/system/docker.service
cat <<< "$(jq '."data-root" = "/home/docker"' /etc/docker/daemon.json)" > /etc/docker/daemon.json
systemctl daemon-reload
service docker start
```

And redirect containerd from /var/lib/containerd to /home/containerd:
```
service containerd stop
cd /var/lib
mv containerd /home/containerd
ln -s /home/containerd .
echo 'root = "/var/lib/containerd"' >> /etc/containerd/config.toml
systemctl daemon-reload
service containerd start
```

Not only do we need to follow the instructions to install the runner:
https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service

Alternatively:
https://github.com/vbem/multi-runners

But also set/enable SELinux contexts:
https://github.com/actions/runner/issues/410

