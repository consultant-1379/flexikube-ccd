ip link set docker0 down
ip link delete docker0
iptables --policy INPUT   ACCEPT;
iptables --policy OUTPUT  ACCEPT;
iptables --policy FORWARD ACCEPT;
for table in filter mangle nat raw ; do
  iptables -t $table -Z
  iptables -t $table -F 
  iptables -t $table -X 
done
