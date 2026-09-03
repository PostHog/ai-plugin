> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Kubernetes metrics installation - Docs

Copy page

# Kubernetes metrics installation - Docs

> **Note:** Metrics is in alpha. Setup details, including the ingestion endpoint, may change before general availability.

If your Kubernetes workloads already expose Prometheus-format `/metrics` endpoints, the PostHog metrics agent scrapes them and forwards everything to PostHog. One `helm install`, no application changes.

The agent runs as a single instance by default. To scale beyond one pod, use [shards](#scale-out-with-shards) rather than replicas: two plain replicas would scrape every target twice and double-count all metrics.

1.  1

    ## Prerequisites

    Required

    You need:

    -   A running Kubernetes cluster with `helm` v3 installed
    -   Pods that expose Prometheus metrics (the standard `prometheus.io/scrape: "true"` annotation pattern)
    -   Your PostHog project token

    The chart creates a ClusterRole and ClusterRoleBinding so the agent can discover pods across all namespaces. If your cluster uses strict RBAC policies, confirm you have permission to create cluster-scoped roles.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate metrics requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token**, which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings).

3.  3

    ## Install the Helm chart

    Required

    Terminal

    PostHog AI

    ```bash
    helm install posthog-metrics-agent oci://ghcr.io/posthog/charts/posthog-metrics-agent \
      --set posthog.apiKey=<ph_project_token>
    ```

    For EU Cloud, set the host explicitly:

    Terminal

    PostHog AI

    ```bash
    helm install posthog-metrics-agent oci://ghcr.io/posthog/charts/posthog-metrics-agent \
      --set posthog.apiKey=<ph_project_token> \
      --set posthog.host=https://eu.i.posthog.com
    ```

    If you manage secrets separately, point the chart at an existing Kubernetes Secret containing a `posthog-api-key` key instead of passing the token directly:

    Terminal

    PostHog AI

    ```bash
    helm install posthog-metrics-agent oci://ghcr.io/posthog/charts/posthog-metrics-agent \
      --set posthog.existingSecret=my-posthog-secret
    ```

    The API key is stored in a Secret and injected as an environment variable – it never appears in the ConfigMap.

4.  4

    ## Configure metric discovery

    Required

    ### Annotation discovery (default)

    By default, the agent discovers and scrapes any pod annotated with `prometheus.io/scrape: "true"`. Two optional annotations control the scrape target:

    | Annotation | Default | Description |
    | --- | --- | --- |
    | prometheus.io/scrape | – | Set to "true" to opt a pod in |
    | prometheus.io/path | /metrics | Override the metrics path |
    | prometheus.io/port | Pod's container port | Override the scrape port |

    Example pod annotation:

    YAML

    PostHog AI

    ```yaml
    metadata:
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/custom/metrics"
    ```

    ### Static targets

    For services that don't carry Prometheus annotations, add fixed `host:port` targets:

    Terminal

    PostHog AI

    ```bash
    helm install posthog-metrics-agent oci://ghcr.io/posthog/charts/posthog-metrics-agent \
      --set posthog.apiKey=<ph_project_token> \
      --set 'scrape.staticTargets={my-service:9090,another-service:8080}'
    ```

    You can combine annotation discovery with static targets. To disable annotation discovery entirely and only use static targets, set `scrape.annotationDiscovery=false`.

    ### Extra scrape configs

    For advanced use cases, pass raw Prometheus `scrape_configs` YAML via `scrape.extraScrapeConfigs`. This is appended verbatim to the collector configuration.

5.  5

    ## Verify metrics are flowing

    Recommended

    1.  Confirm the agent pod is running:

    Terminal

    PostHog AI

    ```bash
    kubectl get pods -l app.kubernetes.io/name=posthog-metrics-agent
    ```

    2.  Open [**Metrics**](https://app.posthog.com/metrics) in PostHog and pick a metric from the name picker
    3.  Data points should appear within a minute of the agent starting

    If nothing shows up, check the agent logs for connection or authentication errors:

    Terminal

    PostHog AI

    ```bash
    kubectl logs -l app.kubernetes.io/name=posthog-metrics-agent
    ```

    The agent also exposes its own metrics (scrape successes, queue depth, points sent or dropped) on port `8888`, so you can monitor the monitor.

    [View your metrics in PostHog](https://app.posthog.com/metrics)

6.  6

    ## Keep data through restarts

    Optional

    By default, if PostHog is briefly unreachable the agent retries from memory, and a pod restart during that window drops whatever was buffered. To keep those samples, back the queue with a persistent volume:

    Terminal

    PostHog AI

    ```bash
    --set persistence.enabled=true
    ```

    The chart provisions a volume per agent (using `persistence.size` and `persistence.storageClass`), and samples scraped during an outage survive restarts and deliver when PostHog is reachable again.

7.  7

    ## Scale out with shards

    Optional

    One agent scrapes every target itself, which is enough for most clusters. For a large target set, run a fleet:

    Terminal

    PostHog AI

    ```bash
    --set shards=4
    ```

    The chart switches to a StatefulSet, each pod works out its own shard from its name, and every target is scraped by exactly one pod: nothing is scraped twice, nothing is missed. Combine with `persistence.enabled=true` to give each shard its own durable queue.

9.  ## Next steps

    Checkpoint

    *What you can do with your metrics*

    | Action | Description |
    | --- | --- |
    | [Why you need metrics](/docs/metrics/basics.md) | What metrics show you that events and logs don't |
    | [Getting started guide](/docs/metrics/start-here.md) | Pick the right metric type, add attributes carefully, and chart what matters |
    | Group and filter | Group by an attribute for one line per value, or filter with key=value chips |
    | [How metrics works](/docs/metrics/architecture.md) | How metrics are ingested, stored, and queried |
    | Query with SQL | Every metric lands in the posthog.metrics table, queryable from the SQL tab |

    [Continue with the getting started guide](/docs/metrics/start-here.md)

## Configuration reference

| Value | Default | Description |
| --- | --- | --- |
| posthog.apiKey | '' | Project token (phc_...). Stored in a chart-managed Secret |
| posthog.existingSecret | '' | Name of an existing Secret with a posthog-api-key key. Takes precedence over apiKey |
| posthog.host | https://us.i.posthog.com | PostHog ingestion origin. Set to https://eu.i.posthog.com for EU Cloud |
| scrape.interval | 15s | How often to scrape targets |
| scrape.annotationDiscovery | true | Discover pods via prometheus.io/scrape annotations |
| scrape.staticTargets | [] | Fixed host:port targets, e.g. ['my-svc:9090'] |
| scrape.extraScrapeConfigs | '' | Raw Prometheus scrape_configs YAML appended verbatim |
| shards | 1 | Agent fleet size. Above 1, a StatefulSet partitions targets so each is scraped once |
| persistence.enabled | false | Buffer undelivered batches on a persistent volume so restarts lose nothing |
| persistence.size | 10Gi | Size of each agent's queue volume |
| persistence.storageClass | '' | StorageClass for the queue volume. Empty uses the cluster default |
| podEnv | {} | Extra environment variables for the agent container |
| resources.requests.cpu | 100m | CPU request |
| resources.requests.memory | 256Mi | Memory request |
| resources.limits.memory | 512Mi | Memory limit |
| rbac.create | true | Create a ClusterRole for pod discovery |
| serviceAccount.create | true | Create a dedicated ServiceAccount |
| serviceAccount.name | '' | Override the ServiceAccount name. Required when serviceAccount.create is false |
| nodeSelector | {} | Kubernetes node selector |
| tolerations | [] | Kubernetes tolerations |
| affinity | {} | Kubernetes affinity rules |

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better