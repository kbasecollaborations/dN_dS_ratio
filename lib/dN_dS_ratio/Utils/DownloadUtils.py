import os
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.VariationUtilClient import VariationUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil


class DownloadUtils:
    def __init__(self, callbackURL):
        self.callbackURL = os.environ['SDK_CALLBACK_URL']
        self.au = AssemblyUtil(self.callbackURL)
        self.vu = VariationUtil(self.callbackURL)
        self.gfu = GenomeFileUtil(self.callbackURL)
        pass

    def download_genome(self, genomeref, output_dir):
        '''
        this funciton downloads genome.
        :param genomeref:
        :param output_dir:
        :return:
        '''

        file = self.au.get_assembly_as_fasta({
          'ref': genomeref,
          'filename': os.path.join(output_dir, "ref_genome.fa")
        })
        return file

    def get_variation(self, variation_ref):
        '''
        This function downloads variations.
        :param variation_ref:
        :param filename:
        :return:
        '''

        filepath = self.vu.get_variation_as_vcf({
            'variation_ref': variation_ref
        })['path']
        return filepath

    def get_gff(self, genome_ref):
        file = self.gfu.genome_to_gff({'genome_ref': genome_ref})
        return file['file_path']

    def get_assembly(self, assembly_ref):
        file = self.au.get_assembly_as_fasta({
          'ref': assembly_ref
        })
        return file['path']
