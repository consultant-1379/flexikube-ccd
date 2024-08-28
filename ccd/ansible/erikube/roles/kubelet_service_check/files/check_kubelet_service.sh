#!/bin/bash
set -e

create_check_kubelet_script()
{
    FILE=/usr/bin/check_kubelet_service.sh
    if [ ! -e $FILE ]; then
    cat <<EOF >$FILE
#!/bin/bash

SERVICENAME="kubelet.service"
systemctl is-active --quiet \$SERVICENAME
STATUS=\$? # return value is 0 if running
if [[ "\$STATUS" -ne "0" ]]; then
    echo "Service '\$SERVICENAME' is not curently running... Starting now..."
    systemctl restart \$SERVICENAME
fi
EOF
    chmod 755 $FILE
    fi
}

# This function creates and adds the cron job for checking kubelet.service status and restartes if dead/stop
create_kubelet_script_cron_job()
{
    command="/usr/bin/check_kubelet_service.sh"
    job="* * * * * for i in {1..6}; do $command & sleep 10; done"
    cat <(fgrep -i -v "$command" <(crontab -l)) <(echo "$job") | crontab -
}


create_check_kubelet_script
create_kubelet_script_cron_job
