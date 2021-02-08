import uuid
import os
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport

class htmlreportutils:
    def __init__(self):
        pass

    def import_image(self, dn_ds_report, output_dir):
        '''
        function for adding venn_diagram to report
        :param output_dir:
        :return: image path
        '''

        output = "<html><head></head><body>"
        output += "<h2>Dn/Ds Report</h2>"
        output += "<table>"
        with open(os.path.join(output_dir, "dnds_statistics.tsv"), 'r') as fp:
            for line in fp:
                (col1, col2) = line.split("\t")
                output += "<tr><td>" + col1 + "</td><td>" + col2 + "</td></tr>"
        output += "</table></body></html>"
        return output

    def create_html_report(self, callback_url, output_dir, workspace_name):
        '''
        function for creating html report
        :param callback_url:
        :param output_dir:
        :param workspace_name:
        :return: report
        '''

        dfu = DataFileUtil(callback_url)
        report_name = 'kb_dnds_report_' + str(uuid.uuid4())
        report = KBaseReport(callback_url)
        htmlstring = self.import_image("dn_ds_report", output_dir)

        try:
            with open(output_dir +"/index.html" , "w") as html_file:
               html_file.write(htmlstring +"\n")
        except IOError:
            print("Unable to write "+ index_file_path + " file on disk.")

        report_shock_id = dfu.file_to_shock({'file_path': output_dir,
                                            'pack': 'zip'})['shock_id']

        html_file = {
            'shock_id': report_shock_id,
            'name': 'index.html',
            'label': 'index.html',
            'description': 'HTMLL report for Variation Comparision'
            }
        
        report_info = report.create_extended_report({
                        'direct_html_link_index': 0,
                        'html_links': [html_file],
                        'report_object_name': report_name,
                        'workspace_name': workspace_name
                    })
        return {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }


