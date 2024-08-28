rm -rf /var/lib/{kubelet,etcd} /etc/{kubernetes,etcd,cni}
rm -f /etc/systemd/system/etcd* /etc/sysconfig/docker*
set +e
sudo umount overlay
sudo umount overlay2
rm -rf /var/lib/docker /usr/local/{bin,lib,etc,opt}/*
