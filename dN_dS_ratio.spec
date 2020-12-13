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
    funcdef run_dN_dS_ratio(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
