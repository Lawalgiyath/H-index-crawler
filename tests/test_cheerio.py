import os
from apify_client import ApifyClient
client = ApifyClient('YOUR_APIFY_TOKEN')
run = client.actor('apify/cheerio-scraper').call(run_input={
    'startUrls': [{'url': 'https://scholar.google.com/citations?user=bKfZRvMAAAAJ&hl=en'}],
    'pageFunction': '''
    async function pageFunction(context) {
        const { $ } = context;
        let citations = [];
        $("#gsc_rsb_st tr").each((i, row) => {
            citations.push($(row).text());
        });
        return { citations: citations };
    }
    '''
})
print([i for i in client.dataset(run['defaultDatasetId'] if isinstance(run, dict) else run.default_dataset_id).iterate_items()])

