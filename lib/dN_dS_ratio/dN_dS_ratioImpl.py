# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import uuid
from dN_dS_ratio.Utils.DownloadUtils import DownloadUtils
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
        assembly_path = self.du.get_assembly(assembly_ref)

        gff_ref = params['genome_ref']
        gff_path = self.du.get_gff(gff_ref)

        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[]},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
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
