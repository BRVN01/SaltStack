#!/usr/bin/env python3

import json
import sys
import os

arg_len = len(sys.argv)-1

if not ((arg_len > 1) and (arg_len <= 2)):
    print("Erro, número de argumentos inválido")
    sys.exit(10)

# Joga os argumentos para variáveis:
sector_arg1 = sys.argv[1]
machinetype_arg2 = sys.argv[2]

# Tratativa de erro para caso do tipo de maquina não existir:
if not ((machinetype_arg2 == 'desktops') or (machinetype_arg2 == 'laptops')):
    print('Machine type', machinetype_arg2, 'not found!')
    sys.exit(10)

# Tratativa de erro para caso do setor não existir:
stream_groups = os.popen('ls /var/log/salt-report/'+machinetype_arg2)
output_groups = stream_groups.readlines()

if sector_arg1+'\n' not in output_groups:
    print('Sector', sector_arg1, 'not found!')
    sys.exit(10)

# Pega os arquivos dentro de report de cada maquina:
stream = os.popen('ls /var/log/salt-report/'+machinetype_arg2+'/'+sector_arg1+'/*.log 2>/dev/null')
output = stream.readlines()

if not output:
    print('No files were found!')
    sys.exit(10)

def collect(report):
    updates = ''
    categorias = ''
    title = ''

    message = """\n######################\n# System Information #\n######################\n"""


    lines_system = """Name: {0}\nMachine type: {1}\nSector: {2}\nBios Detail: {3}\nOS Version: {4}\nCollection Date: {5}\nInstall Date: {6}\nUsers: {7}"""

    nome = str(report['SystemInfo']['name'])
    machinetype = str(report['SystemInfo']['MachineType'])
    sector = str(report['SystemInfo']['sector'])
    bios_detail = str(report['SystemInfo']['bios_details'])
    os_version = str(report['SystemInfo']['os_version'])
    collection_date = str(report['SystemInfo']['collection_date'])
    install_date = str(report['SystemInfo']['install_date'])
    users = str(report['SystemInfo']['users'])

    print(message + '\n' + lines_system.format(nome, machinetype, sector, bios_detail, os_version, collection_date, install_date, users))

    if report['Updates'] != 'Nothing to return':
        
        for chave in report['Updates'].keys():
            updates += str(report['Updates'][chave]['KBs']) + '\n'
            title += str(report['Updates'][chave]['Title']) + '\n'
            categorias += str(report['Updates'][chave]['Categories']) + '\n'

        message = """\n######################\n# Update Information #\n######################\n"""

        lines_update = """Updates available: \n{0}\nCategory: \n{1}\nUpdate Title: \n{2}"""

        print(message + '\n' + lines_update.format(updates, categorias, title))

    else:

        message = """\n######################\n# Update Information #\n######################\n"""
        print(message + '\n' + 'Windows updated!')

for fileslog in output:
    
    # Removendo '\n' do nome do arquivo:
    fileslog = fileslog.strip()

    # Abrindo o arquivo JSON:
    with open(fileslog, 'r') as f:
        # Retorna o JSON como um dicionário Python:
        reportJson = json.load(f)

    collect(reportJson)

    print('_________________________________________________________________________')

    # Fechando o arquivo aberto:
    f.close()
