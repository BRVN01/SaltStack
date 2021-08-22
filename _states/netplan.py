import os

def create(
        name,
        filename=None,
        macaddress=None, 
        addresses=None, 
        gateway4=None, 
        gateway6=None,
        nameservers=None,
        dhcp4=False,
        dhcp6=False,
        acceptra=False,
):

    if gateway4 is not None:
        if dhcp4:
            ret = {
                "name": name,
                "changes": {},
                "result": False,
                "comment": "DHCP4 and gateway4 is set up",
            }
            return ret

        else:
            dhcp4 = None

    if gateway6 is not None:
        if dhcp6:
            ret = {
                "name": name,
                "changes": {},
                "result": False,
                "comment": "DHCP6 and gateway6 is set up",
            }
            return ret

        else:
            dhcp6 = None

    if addresses is not None:
        if dhcp4:
            ret = {
                "name": name,
                "changes": {},
                "result": False,
                "comment": "DHCP4 and addresses is set up",
            }
            return ret 

        if dhcp6:
            ret = {
                "name": name,
                "changes": {},
                "result": False,
                "comment": "DHCP6 and addresses is set up",
            }
            return ret

    if filename is not None:
       filename = '/etc/netplan/' + filename

    else:
        filename = "/etc/netplan/10-network_salt.yaml"


    if nameservers is not None:
       spaces = ' '*24
       spaces = spaces + '- '
       nameservers = '\n- '.join(nameservers)
       nameservers = nameservers.replace("- ", spaces)
       nameservers = '- ' + nameservers

    if acceptra is False:
       acceptra = "false"

    a = """network:
        version: 2
        ethernets:
            {0}:
                macaddress: {8}
                addresses: [{1}]
                dhcp4: {2}
                dhcp6: {3}
                gateway4: {4}
                gateway6: {5}
                accept-ra: {6}
                nameservers:
                    addresses:
                        {7}\n""".format(
                            name,
                            addresses,
                            dhcp4,
                            dhcp6,
                            gateway4,
                            gateway6,
                            acceptra,
                            nameservers,
                            macaddress)
    arq = open(filename, 'w')
    arq.write(a)
    arq.close()

    arq = open(filename, 'r')
    d = arq.readlines()
    arq.close()

    arq = open(filename, 'w')
    for line in d:
        if "False" not in line: 
            if "None" not in line:
                if nameservers is None:
                    if "nameservers" not in line:
                        if "addresses:\n" not in line:
                            arq.write(line)
                else:
                    arq.write(line)
                    
    arq.close()

    if os.path.exists(filename):
        ret = {
            "name": name,
            "changes": {},
            "result": True,
            "comment": "{} has been created".format(filename),
        }

    return ret
