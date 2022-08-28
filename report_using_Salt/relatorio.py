#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import json
import sys
import os

class Report:
          
    def __init__(self): 

        if not ((len(sys.argv)-1 > 1) and (len(sys.argv)-1 <= 2)):
            print("Erro, número de argumentos inválido")
            sys.exit(9)

        # As veriaveis abaixo herdam os argumentos:
        self.sector_arg1 = sys.argv[1]
        self.machinetype_arg2 = sys.argv[2]

        # Tratativa de erro para quando o tipo de maquina digitada não existir (desktop ou laptop):
        if not ((self.machinetype_arg2 == 'desktops') or (self.machinetype_arg2 == 'laptops')):
            print('Machine type', self.machinetype_arg2, 'not found!')
            sys.exit(10)

        # Tratativa de erro para quando o setor digitado não existir:
        stream_sector = os.popen('ls /var/log/salt-report/'+self.machinetype_arg2)
        sector = stream_sector.readlines()

        if self.sector_arg1+'\n' not in sector:
            print('Sector', self.sector_arg1, 'not found!')
            sys.exit(11)

        # Pega os arquivos dentro de report de cada setor:
        stream_files = os.popen('ls /var/log/salt-report/'+self.machinetype_arg2+'/'+self.sector_arg1+'/*.log 2>/dev/null')
        report_files = stream_files.readlines()

        if not report_files:
            print('No files were found!')
            sys.exit(12)

        self.uptodate = []
        self.outofdate = []

        self.find_files(report_files)


    def find_files(self, report_files):
        # Mostra quantos arquivos de log foram encontrados e quem são:
        if len(report_files) != 0:
            message_total_files = """\n######################\n# Total files found  #\n######################\n"""
            print(message_total_files + '\n' + 'For sector', self.sector_arg1, 'We have a total of:', len(report_files), 'file(s)')

            message_hosts_found = """\n########################\n# The Hosts found are  #\n########################\n"""
            hosts = ''

            for fileshost in report_files:
    
                # Removendo '\n' do nome do arquivo:
                fileshost = fileshost.strip()
                fileshost = fileshost.split('/')
                hosts += fileshost[len(fileshost)-1][0:7] + '\n'
            print(message_hosts_found + '\n' + 'For sector', self.sector_arg1, 'We found the Hosts below:' + '\n' + hosts)

            self.build(report_files)


    def find_update(self, report):

        nome_host = str(report['SystemInfo']['name'])

        if report['Updates'] != 'Nothing to return':
            self.outofdate.append(nome_host)
        
        else:
            self.uptodate.append(nome_host)


    def build(self, report_files):
     
        for fileslog in report_files:
            # Removendo '\n' no nome do arquivo:
            fileslog = fileslog.strip()
    
            # Abrindo o arquivo JSON:
            with open(fileslog, 'r') as f:
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
