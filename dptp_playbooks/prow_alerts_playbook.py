from robusta.api import (
    action,
    PrometheusKubernetesAlert,
    MarkdownBlock,
)

@action
def probe_failing_enricher(event: PrometheusKubernetesAlert):
    print(f"This print will be shown in the robusta logs")
    print(event)
