from robusta.api import *


class FetchLogParams(ActionParams):
    keyword: str


@action
def fetch_log(event: PrometheusKubernetesAlert, params: FetchLogParams):
    print(f"This print will be shown in the robusta logs={event} params={params}")

    # TODO: somehow fetch prow job logs

    event.add_enrichment([
        MarkdownBlock(f'fetch logs for event {event} with params {params}')
    ])
