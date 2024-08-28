mount|grep kubelet|cut -d\  -f3|xargs umount
systemctl daemon-reload
