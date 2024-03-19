import time
from typing import List, Optional
from robusta.api import (
    RobustaPod,
)
from hikaru.model.rel_1_26 import (
    EnvVar,
    ObjectMeta,
    PodSpec,
    Container,
)

def exec_in_pod(pod_name: str, node_name: str, debug_image: str,
                cmd: Optional[List[str]]=None, sa: str=None) -> str:
    debugger = create_pod(
        pod_name=pod_name,
        node_name=node_name,
        debug_image=debug_image,
        debug_cmd=cmd,
        sa=sa
        )
    try:
        wait_for_pod_completed(debugger.metadata.name, debugger.metadata.namespace)
    finally:
        logs = debugger.get_logs()
        RobustaPod.deleteNamespacedPod(debugger.metadata.name, debugger.metadata.namespace)
        return logs

def create_pod(
        pod_name: str,
        node_name: str,
        debug_image: str,
        debug_cmd=None,
        env: Optional[List[EnvVar]] = None,
        sa: str = None,
    ) -> "RobustaPod":
        volume_mounts = None
        volumes = None

        pod = RobustaPod(
            apiVersion="v1",
            kind="Pod",
            metadata=ObjectMeta(
                name=pod_name,
                namespace='robusta',
            ),
            spec=PodSpec(
                nodeName=node_name,
                restartPolicy="OnFailure",
                containers=[
                    Container(
                        name="test",
                        image=debug_image,
                        imagePullPolicy="Always",
                        command=debug_cmd,
                        volumeMounts=volume_mounts,
                        env=env,
                    )
                ],
                volumes=volumes,
                serviceAccountName=sa,
            ),
        )

        debugger = pod.createNamespacedPod(pod.metadata.namespace).obj
        return debugger

def wait_for_pod_completed(pod_name: str, namespace: str, timeout: int = 60) -> "RobustaPod":
    for _ in range(timeout):  # retry for up to timeout seconds
        try:
            pod = RobustaPod().read(pod_name, namespace)
            if pod.status.phase == 'Completed':
                return pod
        except KeyError as e:
            if e.status != 404:  # re-raise the exception if it's not a NotFound error
                raise
        time.sleep(1)
    else:
        raise RuntimeError(f"Pod {pod_name} in namespace {namespace} is not ready after {timeout} seconds")
