#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json
import sys
import os

class Report:
          
    def __init__(self): 

        try:
            if sys.argv[1] == '-h' or sys.argv[1] == '--help':
                self.help()
                sys.exit(0)

            elif sys.argv[1] == 'search':
                self.search_minion()
                sys.exit(0)
        
        except IndexError:
            pass

        if not ((len(sys.argv)-1 > 1) and (len(sys.argv)-1 <= 2)):
            print("Error, invalid number of arguments\n")
            self.help()
            sys.exit(9)

        # As veriaveis abaixo herdam os argumentos:
        self.sector_arg1 = sys.argv[1]
        self.machinetype_arg2 = sys.argv[2]

        # Tratativa de erro para quando o tipo de maquina digitada não existir (desktop ou laptop):
        if not ((self.machinetype_arg2 == 'desktops') or (self.machinetype_arg2 == 'laptops')):
            print('Machine type', self.machinetype_arg2, 'not found!')
            sys.exit(10)

        path_machinetype = '/var/log/salt-report/'+self.machinetype_arg2
        sector = os.listdir(path_machinetype)

        if self.sector_arg1 not in sector:
            print('Sector', self.sector_arg1, 'not found!')
            sys.exit(11)

        # Pega os arquivos dentro de report de cada setor:
        self.path_report = '/var/log/salt-report/'+self.machinetype_arg2+'/'+self.sector_arg1+'/'
        report_files = os.listdir(self.path_report)

        if not report_files:
            print('No files were found!')
            sys.exit(12)

        self.uptodate = []
        self.outofdate = []

        self.find_files(report_files)


    def help(self):
        print("Use:\nrelatorio <Sector> <Machine type>\n\nCreate a report using SaltStack and log generated using Shell Script\n\nOptions:\n   Sector - can be sector in the company\n   Machine type - can be 'Desktops' or 'Laptops' (without quotes)\n\nIf you want to use the 'search' option, see below:\n   search <serial>\n\nYou can also use like this:\n   search <serial1> <serial2>...")

    def find_files(self, report_files):
        # Mostra quantos arquivos de log foram encontrados e quem são:
        if len(report_files) != 0:
            message_total_files = """\n######################\n# Total files found  #\n######################\n"""
            print(message_total_files + '\n' + 'For sector', self.sector_arg1, 'We have a total of:', len(report_files), 'file(s)')

            message_hosts_found = """\n########################\n# The Hosts found are  #\n########################\n"""
            hosts = ''

            for fileshost in report_files:
                hosts += fileshost[0:7] + '\n'

            print(message_hosts_found + '\n' + 'For sector', self.sector_arg1, 'We found the Hosts below:' + '\n' + hosts)
            self.build(report_files)


    def search_minion(self):

        if not (len(sys.argv)-1 > 1):
            print("Error, invalid number of arguments in search\n")
            self.help()
            sys.exit(9)

        minions = sys.argv[2:]
        found_files_by_search = []
        not_found_files_by_search = []

        for find in minions:
            find2 = find
            find = find + '.log'

            host_find = self.search_for_files(find, "/var/log/salt-report/")

            if host_find:
                found_files_by_search.append(host_find)
            else:
                not_found_files_by_search.append(find2)

        if len(found_files_by_search) == 0 and len(not_found_files_by_search) >= 0:
            print("\nNo serial found!")
            sys.exit(1)
        elif len(found_files_by_search) >= 1 and len(not_found_files_by_search) >= 1:
            print("\nSome serials could not be found!\nThe serial(s) is/are:\n", not_found_files_by_search)

        #print('found_files_by_search:\n', found_files_by_search)

        for found in found_files_by_search:
            with open(found, 'r') as f:
                # Retorna o JSON como um dicionário Python:
                reportJson = json.load(f)
    
            self.find_info(reportJson)
    
            # Fechando o arquivo aberto:
            f.close() 


    def find_info(self, report):

        host_serial = str(report['SystemInfo']['hardware_serial'])
        host_name = str(report['SystemInfo']['name'])
        host_sector = str(report['SystemInfo']['sector'])

        host_os_version = str(report['SystemInfo']['os_version'])
        host_MachineType = str(report['SystemInfo']['MachineType'])
        host_users = str(report['SystemInfo']['users'])

        print('\n\n######################\n# ', host_serial,'          #\n######################\n')

        print('Serial: {0}\nName: {1}\nSector: {2}\nOS_Version: {3}\nMachine type: {4}\nUsers: {5}'.format(
        host_serial, host_name, host_sector, host_os_version, host_MachineType, host_users))

    def search_for_files(self, filename, search_path):
        result = ''

        # Walking top-down from the /var/log/salt-report/
        for root, dir, files in os.walk(search_path):
            if filename in files:
                result = (os.path.join(root, filename))
        return result


    def find_update(self, report):

        nome_host = str(report['SystemInfo']['hardware_serial'])
        if report['Updates'] != 'Nothing to return':
            self.outofdate.append(nome_host)
        
        else:
            self.uptodate.append(nome_host)


    def build(self, report_files):
     
        for fileslog in report_files:

            # Abrindo o arquivo JSON:
            file_log = self.path_report + fileslog
            with open(file_log, 'r') as f:
                # Retorna o JSON como um dicionário Python:
                reportJson = json.load(f)
    
            self.find_update(reportJson)
    
            # Fechando o arquivo aberto:
            f.close() 

    def print_report(self):
        update = ''
        print()

        if len(self.outofdate) != 0:
            print(len(self.uptodate), 'hosts are up-to-date.')
            print(len(self.outofdate), 'hosts need update. Please do it!')
        
            message_outofdate = """\n######################\n# Hosts Out of Date  #\n######################\n"""

            for out_of_date_hosts in self.outofdate:
                # Removendo '\n' no nome do arquivo:
                update += out_of_date_hosts + '\n'

            print(message_outofdate, '\n'+ update)
        else:
            print('All hosts are up-to-date!')


if __name__ == "__main__":

        init_class = Report()
        init_class.print_report()
