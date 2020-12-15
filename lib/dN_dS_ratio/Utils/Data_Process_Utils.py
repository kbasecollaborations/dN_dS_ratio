import json
import csv
import os
import re
import json
import gzip
import logging
import subprocess

class Data_Process_Utils:

    def __init__(self):
        self.path = "/kb/module/deps"
        pass

    def run_cmd(self, cmd):
        """
        This function runs a third party command line tool
        eg. bgzip etc.
        :param command: command to be run
        :return: success
        """
        command = " ".join(cmd)
        print(command)
        logging.info("Running command " + command)
        cmdProcess = subprocess.Popen(command,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      shell=True)
        for line in cmdProcess.stdout:
            logging.info(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            logging.info('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error in running command with return code: '
                                 + command
                                 + str(cmdProcess.returncode) + '\n')
        logging.info("command " + command + " ran successfully")
        return "success"

    def bgzip_vcf_file(self, filepath):
        bzfilepath = filepath + ".gz"
        command = ["bgzip", filepath]
        self.run_cmd(command)
        return bzfilepath

    def index_vcf_file(self, filepath):
        #bzfilepath = self.bgzip_vcf_file(filepath)
        command  = ["tabix", "-p", "vcf", filepath]
        self.run_cmd(command)
        #return bzfilepath

    def validate_params(self, params):
        if 'genome_ref' not in params:
            raise ValueError('required genome_ref field was not defined')
        elif 'variation_ref' not in params:
            raise ValueError('required variation_ref field was not defined')
        elif 'gene_id' not in params:
            raise ValueError('required gene_id field was not defined') 

    def filter_gff(self, gene_id, gff_path, gff_subsample_path):
        command = ['grep']
        command.append("\'ID=" + gene_id +"\'")
        command.append(gff_path)
        command.extend(['>>', gff_subsample_path])
        self.run_cmd(command)

    def tabix_query(self, filepath, chrom, start, end, subsample_vcf):
        command = ['tabix']
        command.append(filepath)
        command.append(chrom + ":" + start + "-" + end)
        command.extend(['>', subsample_vcf])
        self.run_cmd(command)
