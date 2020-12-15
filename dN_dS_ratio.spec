/*
A KBase module: dN_dS_ratio
*/

module dN_dS_ratio {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */

    typedef structure {
        string workspace_name;
        string variation_ref;
        string genome_ref;
        string gene_id;
    } Inparams;
    funcdef run_dN_dS_ratio(Inparams params) returns (ReportResults output) authentication required;

};
