import os
from apify_client import ApifyClient
client = ApifyClient('YOUR_APIFY_TOKEN')
run = client.actor('apify/cheerio-scraper').call(run_input={
    'startUrls': [{'url': 'https://scholar.google.com/citations?user=bKfZRvMAAAAJ&hl=en'}],
    'pageFunction': '''
    async function pageFunction(context) {
        const { $ } = context;
        let metrics = {
            Citations_All: "0", Citations_Since_2021: "0",
            H_Index_All: "0", H_Index_Since_2021: "0",
            I10_Index_All: "0", I10_Index_Since_2021: "0"
        };
        $("#gsc_rsb_st tr").each((i, row) => {
            const header = $(row).find(".gsc_rsb_sc1").text().trim().toLowerCase();
            const values = $(row).find(".gsc_rsb_std");
            if(header && values.length >= 2) {
                const val_all = $(values[0]).text().trim();
                const val_recent = $(values[1]).text().trim();
                if (header.includes("citations") || header.includes("cited by")) {
                    metrics.Citations_All = val_all;
                    metrics.Citations_Since_2021 = val_recent;
                } else if (header.includes("h-index")) {
                    metrics.H_Index_All = val_all;
                    metrics.H_Index_Since_2021 = val_recent;
                } else if (header.includes("i10-index")) {
                    metrics.I10_Index_All = val_all;
                    metrics.I10_Index_Since_2021 = val_recent;
                }
            }
        });
        return metrics;
    }
    '''
})
print([i for i in client.dataset(run['defaultDatasetId'] if isinstance(run, dict) else run.default_dataset_id).iterate_items()])

