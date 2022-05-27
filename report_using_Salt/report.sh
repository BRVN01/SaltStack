#!/bin/bash

date=$(date +%F_%T)

if [ $# -ne '0' ];then
	echo "Unknown argument!"
	exit 2
fi

laptop_save="/var/log/salt-report/laptops/"
desktop_save="/var/log/salt-report/desktops/"

LaptopsGroups="$(grep -o ".*-laptops:" /etc/salt/master | sed '/^#/d; s/^  //; s/:$//')"
DesktopsGroups="$(grep -o ".*-desktops:" /etc/salt/master | sed '/^#/d; s/^  //; s/:$//')"

collect_info () {
	# Filtra apenas os hosts que estão up:
	local hosts_up="$(grep 'true' <<<"$1" | cut -d '"' -f 2)"
    local sector="$2"
    local MachineType="$3"

    if [[ ${MachineType} == "laptops" ]];then

        local_save="${laptop_save}${sector}/"

        if [[ ! -e "${laptop_save}${sector}" ]]; then
            mkdir -p ${laptop_save}${sector}
        fi
    else

        local_save="${desktop_save}${sector}/"

        if [[ ! -e "${desktop_save}${sector}" ]]; then
            mkdir -p ${desktop_save}${sector}
        fi
    fi

	# Loop que usa apenas hosts up para gerar relatorio:
	for host in ${hosts_up}; do

        # ${host} recebe o nome da máquina
		local SystemInfo=$(salt "${host}" system.get_system_info --out=json)
        local SystemInfo=$(echo "${SystemInfo}" | sed -e "3 a .        \"collection_date\": \"${date}\"," -e "s/\"${host}\":/\"SystemInfo\":/" -e '$ d' | sed "$ d" | sed '$ s/$/&,/')
        local SystemInfo=$(echo "${SystemInfo}" | sed -e "3 a .        \"sector\": \"${sector}\"," | sed "3 a .        \"MachineType\": \"${MachineType}\",")
        local SystemInfo=$(sed 's/true/"true"/; s/false/"false"/; /null/d; s/^\.//' <<<"${SystemInfo}")

		local users=$(salt "${host}" user.list_users --out=json)
        local users=$(echo "${users}" | sed "s/^\.//; s/\"${host}\":/\"users\":/; s/^/    /; 1d; s/}/},/")

		local updates=$(salt "${host}" win_wua.list --out=json)
        local updates=$(echo "${updates}" | sed 's/            /        /' | sed "s/^\.//; s/\"${host}\":/\"Updates\":/;1d")
        local updates=$(sed 's/true/"true"/; s/false/"false"/; /null/d' <<<"${updates}")

		echo "${SystemInfo}
${users}
${updates}" > ${local_save}${host}.log
	done

}


check_ping () {
    groups_join_names="${LaptopsGroups} ${DesktopsGroups}"

    for GName in ${groups_join_names}
    do
        status_host="$(salt -N ${GName} test.ping --out=json 2>/dev/null | sed -r 's/^ +/   /; s/^[}{]$//; /^$/d')"

	    local up=$(grep -c "true" <<<${status_host})
	    local down=$(grep -vc "true" <<<${status_host})

        Just_GName=$(sed 's/-desktops\|-laptops//' <<<${GName})
        Just_GType=$(echo ${GName} | cut -d '-' -f2)

        collect_info "${status_host}" "${Just_GName}" "${Just_GType}"


	    echo -e "\nHosts Status - ${date}\n${status_host}
        Total Hosts: $(($up+$down))
        Total UP: ${up}
        Total Down: ${down}" >> /var/log/salt-report/${GName}.ping

	    echo "$(printf "%0.s*" $(seq 79 $n))" >> /var/log/salt-report/${GName}.ping
    done
}

check_ping
