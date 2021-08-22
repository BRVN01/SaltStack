import salt.utils.json
import salt.pillar
import salt.utils.crypt
import json
import ast
import os

def create(*args, **kwargs):
    # Preserve backwards compatibility
    if args:
        return item(*args)

    pillarenv = kwargs.get("pillarenv")
    if pillarenv is None:
        if __opts__.get("pillarenv_from_saltenv", False):
            pillarenv = kwargs.get("saltenv") or __opts__["saltenv"]
        else:
            pillarenv = __opts__["pillarenv"]

    pillar_override = kwargs.get("pillar")
    pillar_enc = kwargs.get("pillar_enc")

    if pillar_override and pillar_enc:
        try:
            pillar_override = salt.utils.crypt.decrypt(
                pillar_override,
                pillar_enc,
                translate_newlines=True,
                opts=__opts__,
                valid_rend=__opts__["decrypt_pillar_renderers"],
            )
        except Exception as exc:  # pylint: disable=broad-except
            raise CommandExecutionError(
                "Failed to decrypt pillar override: {}".format(exc)
            )

    name_id = __grains__['id'].lower()
    pillar = salt.pillar.get_pillar(
        __opts__,
        dict(__grains__),
        __opts__["id"],
        pillar_override=pillar_override,
        pillarenv=pillarenv,
    )

    dict_pillar = salt.utils.json.dumps(pillar.compile_pillar())
    dict_pillar = ast.literal_eval(dict_pillar)

    key_pillar = str(dict_pillar.keys())
    key_pillar = key_pillar.replace('dict_keys([', '')
    key_pillar = key_pillar.replace("'])", "")
    key_pillar = key_pillar.replace("'", "")

    dict_keys = dict_pillar[key_pillar][__opts__["id"]]
    Values = dict_pillar[key_pillar][__opts__["id"]]

    if "interface" not in dict_keys.keys():
        dict_keys["interface"] = "enpXXX"

    if "macaddress" not in dict_keys.keys():
        dict_keys["macaddress"] = "None"

    if "ipv6" not in dict_keys.keys():
        dict_keys["ipv6"] = "False"

    if "ipv4" not in dict_keys.keys():
        dict_keys["ipv4"] = "False"

    if "addresses" not in dict_keys.keys():
        ret = {
            "Values": Values,
            "result": False,
            "comment": "Address IP empty",
        }
        return ret

    if "gateway4" not in dict_keys.keys():
        if dict_keys["ipv4"] is True:
            ret = {
                "Values": Values,
                "result": False,
                "comment": "Gateway4 empty",
            }
            return ret
        else:
            dict_keys["gateway4"] = None

    if "gateway6" not in dict_keys.keys():
        if dict_keys["ipv6"] is True:
            ret = {
                "Values": Values,
                "result": False,
                "comment": "Gateway6 empty",
            }
            return ret
        else:
            dict_keys["gateway6"] = None

    if "dhcp4" not in dict_keys.keys():
        dict_keys["dhcp4"] = "False"

    if "dhcp6" not in dict_keys.keys():
        dict_keys["dhcp6"] = "False"

    if "filename" in dict_keys.keys():
       dict_keys["filename"] = '/etc/netplan/' + dict_keys["filename"]

    else:
        dict_keys["filename"] = "/etc/netplan/10-network_salt.yaml"

    if "nameservers" in dict_keys.keys():
        spaces = ' '*24
        spaces = spaces + '- '
        dict_keys["nameservers"] = dict_keys["nameservers"].replace(", ", "\n- ")
        dict_keys["nameservers"] = dict_keys["nameservers"].replace("- ", spaces)
        dict_keys["nameservers"] = '- ' + dict_keys["nameservers"]
    else:
        dict_keys["nameservers"] = None

    if "acceptra" not in dict_keys.keys():
       dict_keys["acceptra"] = "false"

    netplan_file = """network:
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
                            dict_keys["interface"],
                            dict_keys["addresses"],
                            dict_keys["dhcp4"],
                            dict_keys["dhcp6"],
                            dict_keys["gateway4"],
                            dict_keys["gateway6"],
                            dict_keys["acceptra"],
                            dict_keys["nameservers"],
                            dict_keys["macaddress"])

    arq = open(dict_keys["filename"], 'w')
    arq.write(netplan_file)
    arq.close()

    arq = open(dict_keys["filename"], 'r')
    d = arq.readlines()
    arq.close()

    arq = open(dict_keys["filename"], 'w')
    for line in d:
        if "False" not in line: 
            if "None" not in line:
                if dict_keys["nameservers"] is None:
                    if "nameservers" not in line:
                        if "addresses:\n" not in line:
                            arq.write(line)
                else:
                    arq.write(line)
                    
    arq.close()

    if os.path.exists(dict_keys["filename"]):
        ret = {
            "Values": Values,
            "result": True,
            "comment": "{} has been created".format(dict_keys["filename"]),
        }

    return ret
#    return netplan_file
