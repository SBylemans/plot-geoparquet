from hera.workflows import DAG, Task, Workflow, WorkflowsService, Container, Step, Artifact, SecretEnv, Env, Parameter
from hera.workflows.models import WorkflowMetadata
from hera.events.models import EventSource, EventSourceSpec, S3Artifact, Event, Sensor, ArgoWorkflowTrigger, \
    StandardK8STrigger, FileArtifact, ArtifactLocation, S3Bucket, SensorSpec, Trigger, TriggerTemplate, EventDependency, \
    Resource, TriggerParameter, TriggerParameterSource
from hera.workflows.models import WorkflowMetadata, PodGC, SecretKeySelector, ObjectMeta
from hera.shared import global_config
import yaml

with Workflow(
        generate_name="plot-geoparquet-",
        entrypoint="dag",
        namespace="gis-team",
        workflow_metadata=WorkflowMetadata(labels={
            "team": "gis"
        }),
        arguments=[
            Parameter(name="key", value="OVERRIDEN")
        ]
) as w:
    Container(name="container-template",
              image="ghcr.io/sbylemans/plot-geoparquet",
              env=[
                  SecretEnv(name="AWS_ACCESS_KEY_ID", secret_key="artifacts-minio", secret_name="access-key"),
                  SecretEnv(name="AWS_SECRET_ACCESS_KEY", secret_key="artifacts-minio", secret_name="secret-key"),
                  Env(name="BOTO3_ENDPOINT_URL", value="http://minio:11000"),
              ],
              args=["{{inputs.parameters.key}}"])
    with DAG(name="dag") as s:
        t1 = Task(name="plot", template="container-template")

    e = EventSource(
        metadata=ObjectMeta(name="minio"),
        spec=EventSourceSpec(
            minio={
                'geoparquet': S3Artifact(bucket=S3Bucket(key="artifacts-minio", name="bucket"),
                                         endpoint="http://minio:11000",
                                         access_key=SecretKeySelector(key="access-key", name="artifacts-minio"),
                                         secret_key=SecretKeySelector(key="secret-key", name="artifacts-minio"),
                                         events=[
                                             "s3:ObjectCreated:Put",
                                             "s3:ObjectRemoved:Delete"
                                         ],
                                         insecure=True)})
    )
    model = e.dict(exclude_unset=True, exclude_none=True)
    model["apiVersion"] = global_config.api_version
    model["kind"] = e.__class__.__name__

    yaml_output = yaml.dump(model, sort_keys=True, default_flow_style=False)
    print(yaml_output)
    print('---')

    s = Sensor(
        metadata=ObjectMeta(name="minio-sensor"),
        spec=SensorSpec(
            dependencies=[
                EventDependency(name="geoparquet", event_name="geoparquet", event_source_name="minio")],
            triggers=[
                Trigger(
                    template=TriggerTemplate(
                        name="minio-sensor-trigger",
                        argo_workflow=ArgoWorkflowTrigger(operation="submit",
                                                          source=ArtifactLocation(resource=Resource(
                                                              value=w.to_yaml()), ),
                                                          parameters=[
                                                              TriggerParameter(dest="spec.argument.paramaters.0.value", src=TriggerParameterSource(dependency_name="geoparquet", data_key="notification.0.s3.object.key"))
                                                          ])
                    )
                )
            ]
        )
    )

    model = s.dict(exclude_unset=True, exclude_none=True)
    model["apiVersion"] = global_config.api_version
    model["kind"] = s.__class__.__name__

    yaml_output = yaml.dump(model, sort_keys=True, default_flow_style=False)
    print(yaml_output)
