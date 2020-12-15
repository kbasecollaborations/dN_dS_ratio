# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import csv
import uuid
from dN_dS_ratio.Utils.DownloadUtils import DownloadUtils
from dN_dS_ratio.Utils.DnDs_Utils import DnDs_Utils
from dN_dS_ratio.Utils.htmlreportutils import htmlreportutils
from dN_dS_ratio.Utils.Data_Process_Utils import Data_Process_Utils
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
#END_HEADER


class dN_dS_ratio:
    '''
    Module Name:
    dN_dS_ratio

    Module Description:
    A KBase module: dN_dS_ratio
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.du = DownloadUtils(self.callback_url)
        self.pu = DnDs_Utils()
        self.dpu = Data_Process_Utils()
        self.hu = htmlreportutils()
        self.config = config

       
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_dN_dS_ratio(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_dN_dS_ratio
        print(params)
        #self.SU.validate_params(params)
        
        workspace = params['workspace_name']
        output_dir = os.path.join(self.shared_folder, str(uuid.uuid4()))
        os.mkdir(output_dir)
        self.ws_url = self.config['workspace-url']
        self.ws = Workspace(url=self.ws_url, token=ctx['token'])
        

        
        variation_ref = params['variation_ref']
        variation = self.du.get_variation(variation_ref)
        self.du.tabix_index(variation)

        variation_obj = self.ws.get_objects2({'objects': [{'ref': variation_ref}]})['data'][0]


        data = self.ws.get_objects2( {'objects':[{"ref":variation_ref, 'included': ['/sample_set_ref']}]})['data'][0]['data']
        sample_set_ref = data['sample_set_ref']

        assembly_ref = variation_obj['data']['assembly_ref']
        assembly_path = self.du.get_assembly(assembly_ref, output_dir)
        
        gff_ref = params['genome_ref']
        gff_path = self.du.get_gff(gff_ref)

        gene_id = params['gene_id']

        gff_subsample_path = os.path.join(output_dir, "sub_sample.gff")
        #cmd = 'grep ID=' + gene_id + ' ' + gff_path + ' >> ' + gff_subsample_path
        #os.system(cmd)

        self.dpu.filter_gff(gene_id, gff_path, gff_subsample_path)
        

        with open(gff_subsample_path, 'r') as f:
            line =  f.readline() 
            rec  = line.split("\t")
            chrom = rec[0]
            start = rec[3]
            end = rec[4]

    
        sub_sample_vcf = os.path.join(output_dir, "sub_sample.vcf")
          
        #temporary test function
        #index_cmd = "tabix -p vcf " + variation
        #os.system(index_cmd)

        self.dpu.index_vcf_file(variation)

        self.dpu.tabix_query(variation, chrom, start, end, sub_sample_vcf)
      

        #tabix_cmd = "tabix " + variation + " " + chrom + ":" +start + "-" + end + " > " + sub_sample_vcf
        #os.system(tabix_cmd)

        #vcf_subsample = self.du.tabix_query(variation, chrom, start, end, output_dir) 
        #print(vcf_subsample)

        #end of test function
        
         
        #outout_dir = '/kb/module/work/09f432d2-9e76-4ad1-b78a-8fa25693777c'
        assembly_path = output_dir + '/ref_genome.fa'
        variation = output_dir + '/sub_sample.vcf'
        gff_path = output_dir + '/sub_sample.gff'
        

        sequence =  self.pu.read_refseq(assembly_path)
        print(sequence)

        var_list = self.pu.read_vcf(variation, sequence)

        print(var_list)
        
        #if os.path.exists("variant_info.tsv"):
        #   os.remove("variant_info.tsv")

        var_file = os.path.join(output_dir, "variant_info.tsv")

        with open(var_file, 'w') as variant_tmp_file:
           var_temp = csv.writer(variant_tmp_file, delimiter='\t')
           var_temp.writerow(["#chr", "ref", "alt", "pos", "codon number", "pos in codon", "codon start", "codon", "mutation type", "coverage"])
           for var_gene_list in var_list:
              var_temp.writerow(var_gene_list)

        gff_data = self.pu.read_gff_file(gff_path)



        codon_list = self.pu.get_triplets(sequence, gff_data)
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        #exit(codon_list)

        codon_result_file =  os.path.join(output_dir, "codon_results_temp.tsv")
        corrected_codon_result_file =  os.path.join(output_dir, "corrected_variant_info.tsv")
        
        #if os.path.exists("codon_results_temp.tsv"):
        #   os.remove("codon_results_temp.tsv")
        with open(codon_result_file, 'w') as cdr_tmp_file:
            cdr_temp = csv.writer(cdr_tmp_file, delimiter='\t')
            cdr_temp.writerow(["#chr", "gene", "codon", "codon start", "codon end", "codon positions", "codon number", "N", "S"])
            for gene_codon_list in codon_list:
                for codon in gene_codon_list:
                    cdr_temp.writerow(codon)

        merged_list = self.pu.merge_files(corrected_codon_result_file, codon_result_file, var_file)
        all_possible_codon = self.pu.get_all_possible_codon(merged_list)  # generating all possible codon

        self.pu.generate_statistics(corrected_codon_result_file, codon_result_file, all_possible_codon, output_dir)

        ############# html reporting ############################################################3 
        workspace = params['workspace_name']
        output = self.hu.create_html_report(self.callback_url, output_dir, workspace)

        #report = KBaseReport(self.callback_url)
        #report_info = report.create({'report': {'objects_created':[]},
        #                                        'workspace_name': params['workspace_name']})
        #output = {
        #    'report_name': report_info['name'],
        #    'report_ref': report_info['ref'],
        #}
        #END run_dN_dS_ratio

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_dN_dS_ratio return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
