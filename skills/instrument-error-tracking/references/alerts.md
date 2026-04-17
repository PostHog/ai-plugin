# Send error tracking alerts - Docs

To stay on top of issues, you can set up alerts. These enable you to post to Slack, Discord, Teams, or an HTTP Webhook when an issue is created or reopened.

## Issue created or reopened

To alert when an issue is created or reopened, go to [error tracking's configuration page](https://app.posthog.com/error_tracking/configuration#selectedSetting=error-tracking-alerting) and click **Alerting**. This shows you a list of existing alerts. Clicking **New notification** brings you to a page to create a new one.

![Error tracking alerting](https://res.cloudinary.com/dmukukwp6/image/upload/error_alerts_create_light_1a05deef21.png)![Error tracking alerting](https://res.cloudinary.com/dmukukwp6/image/upload/error_alerts_create_dark_7585087b18.png)

Choosing an option brings you to a page to configure the alert. This may require setting up the Slack integration or pasting in a webhook URL. Once done, you can test the alert by clicking **Test function** and then finalize by clicking **Create & enable**.

This will then send alerts to your chosen destination when an issue is created or reopened like this:

## Issue properties and assignments

You can filter an alert based on the properties of an issue. This is useful for notifying a specific team when they have been auto assigned an issue using [auto assignment rules](/docs/error-tracking/managing-issues.md#auto-assignment-rules).

![Error tracking alert assignee filtering](https://res.cloudinary.com/dmukukwp6/image/upload/assignee_filter_light_e575af6512.png)![Error tracking alert assignee filtering](https://res.cloudinary.com/dmukukwp6/image/upload/assignee_filter_dark_9a8907af03.png)

## Spike alerts

PostHog can also alert you when an existing issue suddenly spikes in volume - for example, after a bad deploy. This works differently from issue-created alerts. Instead of triggering when a new issue is first seen, spike alerts fire when an issue's error rate significantly exceeds its historical baseline.

See the [spike detection guide](/docs/error-tracking/spikes.md) to learn how it works and how to configure it.

## Other alerting options

Since error tracking works by capturing `$exception` events, PostHog features that trigger by events can play a role in alerts too.

### Real time destinations

The first way is using [real time destinations](/docs/cdp/destinations.md). This enables you to send events (like `$exception`) to other tools as soon as they are ingested.

To create a real time destination, go to the [data pipelines tab](https://app.posthog.com/data-management/destinations) in PostHog, click **\+ New**, and then select **Destination**. Choose your destination and press **\+ Create**.

On the destination creation screen, make sure to add an event matcher for the `$exception` event, filter for the properties you want, and set the trigger options.

![Real time destination](https://res.cloudinary.com/dmukukwp6/image/upload/http_error_alert_light_9898376c56.png)![Real time destination](https://res.cloudinary.com/dmukukwp6/image/upload/http_error_alert_dark_7705f0e575.png)

Check out our [real time destinations docs](/docs/cdp/destinations.md) for more information.

### Trend alerts

You can also visualize your `$exception` events using [trends](/docs/product-analytics/trends/overview.md). Once you create a trend insight, click the **Alerts** button at the top of the insight and then **New alert**.

Here you can set alerts for event volume value, increase, or decrease.

![Insight alert](https://res.cloudinary.com/dmukukwp6/image/upload/Clean_Shot_2025_04_08_at_14_26_43_2x_4ef6402556.png)![Insight alert](https://res.cloudinary.com/dmukukwp6/image/upload/Clean_Shot_2025_04_08_at_14_25_35_2x_f36353143b.png)

This sends an email notification to the user you choose. Check out our [alerts docs](/docs/alerts.md) for more information.

**Can't find your alert?**

If you'd like a destination to be added that we don't yet support, [let us know in-app](https://app.posthog.com/#panel=support%3Afeedback%3Aerror_tracking%3A%3Afalse).

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better