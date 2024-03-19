from robusta.api import (
    action,
    PrometheusKubernetesAlert,
    MarkdownBlock,
    CallbackBlock,
    CallbackChoice,
    ExecutionBaseEvent,
    Finding,
    FindingSource,
)
from .common import exec_in_pod

@action
def upgrade_cluster_enricher(event: PrometheusKubernetesAlert):
    event.add_enrichment([
        CallbackBlock(
            choices={
                'Start Upgrade': CallbackChoice(action=upgrade_cluster),
            }
        )
    ])

@action
def upgrade_cluster(event: ExecutionBaseEvent):
    logs = exec_in_pod(
        pod_name='cluster-upgrade',
        node_name=None,
        cmd=['oc', 'adm', 'upgrade', '--to-latest'],
        debug_image='registry.ci.openshift.org/ocp/4.15:cli',
        sa='cluster-upgrade-sa',
    )

    finding = Finding(
        title='Cluster upgrade',
        source=FindingSource.CALLBACK,
        aggregation_key='cluster_upgrade'
    )
    finding.add_enrichment([
        MarkdownBlock(f'Cluster upgrade started.'),
        MarkdownBlock(f"{logs}"),
    ])
    event.add_finding(finding)
