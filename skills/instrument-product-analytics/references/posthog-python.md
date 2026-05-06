# PostHog Python SDK

**SDK Version:** 7.14.0

Integrate PostHog into any python application.

## Categories

- Initialization
- Identification
- Capture
- Error Tracking
- Feature flags
- Contexts
- Events
- Client management

## PostHog

This is the SDK reference for the PostHog Python SDK. You can learn more about example usage in the [Python SDK documentation](/docs/libraries/python). You can also follow [Flask](/docs/libraries/flask) and [Django](/docs/libraries/django) guides to integrate PostHog into your project.

### Initialization methods

#### Client()

**Release Tag:** public

Initialize a new PostHog client instance.

### Parameters

- **`project_api_key?`** (`str`) - The project API key.
- **`host`** (`any`) - The host to use for the client.
- **`debug`** (`bool`) - Whether to enable debug mode.
- **`max_queue_size`** (`int`)
- **`send`** (`bool`)
- **`on_error`** (`any`)
- **`flush_at`** (`int`)
- **`flush_interval`** (`float`)
- **`gzip`** (`bool`)
- **`max_retries`** (`int`)
- **`sync_mode`** (`bool`)
- **`timeout`** (`int`)
- **`thread`** (`int`)
- **`poll_interval`** (`int`)
- **`personal_api_key`** (`any`)
- **`disabled`** (`bool`)
- **`disable_geoip`** (`bool`)
- **`historical_migration`** (`bool`)
- **`feature_flags_request_timeout_seconds`** (`int`)
- **`super_properties`** (`any`)
- **`enable_exception_autocapture`** (`bool`)
- **`log_captured_exceptions`** (`bool`)
- **`project_root`** (`any`)
- **`privacy_mode`** (`bool`)
- **`before_send`** (`any`)
- **`flag_fallback_cache_url`** (`any`)
- **`enable_local_evaluation`** (`bool`)
- **`flag_definition_cache_provider?`** (`FlagDefinitionCacheProvider`)
- **`capture_exception_code_variables`** (`bool`)
- **`code_variables_mask_patterns`** (`any`)
- **`code_variables_ignore_patterns`** (`any`)
- **`in_app_modules`** (`UnionType[list[str], any]`)

### Returns

- `None`

### Examples

```python
from posthog import Posthog

posthog = Posthog('<ph_project_api_key>', host='<ph_app_host>')
```

---

### Identification methods

#### alias()

**Release Tag:** public

Create an alias between two distinct IDs.

### Parameters

- **`previous_id?`** (`str`) - The previous distinct ID.
- **`distinct_id?`** (`str`) - The new distinct ID to alias to.
- **`timestamp`** (`any`) - The timestamp of the event.
- **`uuid`** (`any`) - A unique identifier for the event.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this event.

### Returns

- `None`

### Examples

```python
posthog.alias(previous_id='distinct_id', distinct_id='alias_id')
```

---

#### group_identify()

**Release Tag:** public

Identify a group and set its properties.

### Parameters

- **`group_type?`** (`str`) - The type of group (e.g., 'company', 'team').
- **`group_key?`** (`str`) - The unique identifier for the group.
- **`properties?`** (`dict[str, Any]`) - A dictionary of properties to set on the group.
- **`timestamp`** (`datetime`) - The timestamp of the event.
- **`uuid?`** (`str`) - A unique identifier for the event.
- **`disable_geoip?`** (`bool`) - Whether to disable GeoIP for this event.
- **`distinct_id`** (`Number`) - The distinct ID of the user performing the action.

### Returns

- `Optional[str]`

### Examples

```python
posthog.group_identify('company', 'company_id_in_your_db', {
    'name': 'Awesome Inc.',
    'employees': 11
})
```

---

#### set()

**Release Tag:** public

Set properties on a person profile.

### Parameters

- **`kwargs?`** (`Unpack[OptionalSetArgs]`)

### Returns

- `Optional[str]`

### Examples

```python
# Set with distinct id
posthog.set(distinct_id='user123', properties={'name': 'Max Hedgehog'})
```

---

#### set_once()

**Release Tag:** public

Set properties on a person profile only if they haven't been set before.

### Parameters

- **`kwargs?`** (`Unpack[OptionalSetArgs]`)

### Returns

- `Optional[str]`

### Examples

```python
posthog.set_once(distinct_id='user123', properties={'initial_signup_date': '2024-01-01'})
```

---

### Capture methods

#### capture()

**Release Tag:** public

Captures an event manually. [Learn about capture best practices](https://posthog.com/docs/product-analytics/capture-events)

### Parameters

- **`event?`** (`str`) - The event name to capture.
- **`kwargs?`** (`Unpack[OptionalCaptureArgs]`)

### Returns

- `Optional[str]`

### Examples

#### Anonymous event

```python
# Anonymous event
posthog.capture('some-anon-event')
```

#### Context usage

```python
# Context usage
from posthog import identify_context, new_context
with new_context():
    identify_context('distinct_id_of_the_user')
    posthog.capture('user_signed_up')
    posthog.capture('user_logged_in')
    posthog.capture('some-custom-action', distinct_id='distinct_id_of_the_user')
```

#### Set event properties

```python
# Set event properties
posthog.capture(
    "user_signed_up",
    distinct_id="distinct_id_of_the_user",
    properties={
        "login_type": "email",
        "is_free_trial": "true"
    }
)
```

#### Page view event

```python
# Page view event
posthog.capture('$pageview', distinct_id="distinct_id_of_the_user", properties={'$current_url': 'https://example.com'})
```

---

### Error Tracking methods

#### capture_exception()

**Release Tag:** public

Capture an exception for error tracking.

### Parameters

- **`exception?`** (`BaseException`) - The exception to capture.
- **`kwargs?`** (`Unpack[OptionalCaptureArgs]`)

### Returns

- `None`

### Examples

```python
try:
    # Some code that might fail
    pass
except Exception as e:
    posthog.capture_exception(e, 'user_distinct_id', properties=additional_properties)
```

---

### Feature flags methods

#### evaluate_flags()

**Release Tag:** public

Evaluate all feature flags for a user in a single call and return a :class:`FeatureFlagEvaluations` snapshot. Branch on ``.is_enabled()`` / ``.get_flag()`` and pass the same snapshot to :meth:`capture` via the ``flags`` option so events carry the exact flag values the code branched on.  Prefer this over repeated ``get_feature_flag()`` calls and over ``capture(send_feature_flags=True)`` — it consolidates flag evaluation into a single ``/flags`` request per incoming request.  Local evaluation is transparent: when the poller resolves a flag, the snapshot's ``$feature_flag_called`` events are tagged ``locally_evaluated=True`` and reason ``"Evaluated locally"``.

### Parameters

- **`distinct_id`** (`Number`) - The user's distinct ID. If ``None``, falls back to the         context distinct_id. If still unresolvable, returns an empty snapshot.
- **`groups?`** (`dict[str, str]`) - Mapping of group type to group key.
- **`person_properties?`** (`dict[str, Any]`) - Person properties to use for evaluation.
- **`group_properties?`** (`dict[str, dict[str, Any]]`) - Group properties keyed by group type.
- **`only_evaluate_locally`** (`bool`) - If True, never fall back to remote evaluation —         flags that can't be evaluated locally are simply omitted from the snapshot.
- **`disable_geoip?`** (`bool`) - Whether to disable GeoIP lookup.
- **`flag_keys?`** (`list[str]`) - Optional list of flag keys to scope the underlying ``/flags``         request to a subset.
- **`device_id?`** (`str`) - Optional device ID override. If not provided, falls back to the         context device_id (which may be set via tracing headers). Used by         experience-continuity flags to match users across distinct_id changes.

### Returns

- `FeatureFlagEvaluations`

### Examples

```python
flags = posthog.evaluate_flags(
    "user_123",
    person_properties={"plan": "enterprise"},
)
if flags.is_enabled("new-dashboard"):
    render_new_dashboard()
posthog.capture("page_viewed", distinct_id="user_123", flags=flags)
```

---

#### feature_enabled()

**Release Tag:** public

Check if a feature flag is enabled for a user.

### Parameters

- **`key?`** (`any`) - The feature flag key.
- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`send_feature_flag_events`** (`bool`) - Whether to send feature flag events.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `None`

### Examples

```python
is_my_flag_enabled = posthog.feature_enabled('flag-key', 'distinct_id_of_your_user')
if is_my_flag_enabled:
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
```

---

#### get_all_flags()

**Release Tag:** public

Get all feature flags for a user.

### Parameters

- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `Optional[dict[str, Union[bool, str]]]`

### Examples

```python
posthog.get_all_flags('distinct_id_of_your_user')
```

---

#### get_all_flags_and_payloads()

**Release Tag:** public

Get all feature flags and their payloads for a user.

### Parameters

- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `FlagsAndPayloads`

### Examples

```python
posthog.get_all_flags_and_payloads('distinct_id_of_your_user')
```

---

#### get_feature_flag()

**Release Tag:** public

Get multivariate feature flag value for a user.

### Parameters

- **`key?`** (`any`) - The feature flag key.
- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`send_feature_flag_events`** (`bool`) - Whether to send feature flag events.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `Union[bool, str, any]`

### Examples

```python
enabled_variant = posthog.get_feature_flag('flag-key', 'distinct_id_of_your_user')
if enabled_variant == 'variant-key': # replace 'variant-key' with the key of your variant
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
```

---

#### get_feature_flag_payload()

**Release Tag:** public

Get the payload for a feature flag.

### Parameters

- **`key?`** (`any`) - The feature flag key.
- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`match_value`** (`bool`) - The specific flag value to get payload for.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`send_feature_flag_events`** (`bool`) - Deprecated. Use get_feature_flag() instead if you need events.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `None`

### Examples

```python
is_my_flag_enabled = posthog.feature_enabled('flag-key', 'distinct_id_of_your_user')

if is_my_flag_enabled:
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
```

---

#### get_feature_flags_and_payloads()

**Release Tag:** public

Get feature flags and payloads for a user.

### Parameters

- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `FlagsAndPayloads`

### Examples

```python
result = posthog.get_feature_flags_and_payloads('<distinct_id>')
```

---

#### get_feature_payloads()

**Release Tag:** public

Get feature flag payloads for a user.

### Parameters

- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `dict[str, str]`

### Examples

```python
payloads = posthog.get_feature_payloads('<distinct_id>')
```

---

#### get_feature_variants()

**Release Tag:** public

Get feature flag variants for a user.

### Parameters

- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `dict[str, Union[bool, str]]`

---

#### get_flags_decision()

**Release Tag:** public

Get feature flags decision.

### Parameters

- **`distinct_id`** (`Number`) - The distinct ID of the user.
- **`groups?`** (`dict`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`flag_keys_to_evaluate?`** (`list[str]`) - A list of specific flag keys to evaluate. If provided,         only these flags will be evaluated, improving performance.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `FlagsResponse`

### Examples

```python
decision = posthog.get_flags_decision('user123')
```

---

#### load_feature_flags()

**Release Tag:** public

Load feature flags for local evaluation.

### Returns

- `None`

### Examples

```python
posthog.load_feature_flags()
```

---

### Other methods

#### flush()

**Release Tag:** public

Force a flush from the internal queue to the server. Do not use directly, call `shutdown()` instead.

### Returns

- `None`

### Examples

```python
posthog.capture('event_name')
posthog.flush()  # Ensures the event is sent immediately
```

---

#### get_feature_flag_result()

**Release Tag:** public

Get a FeatureFlagResult object which contains the flag result and payload for a key by evaluating locally or remotely depending on whether local evaluation is enabled and the flag can be locally evaluated. This also captures the `$feature_flag_called` event unless `send_feature_flag_events` is `False`.

### Parameters

- **`key?`** (`any`) - The feature flag key.
- **`distinct_id?`** (`any`) - The distinct ID of the user.
- **`groups`** (`any`) - A dictionary of group information.
- **`person_properties`** (`any`) - A dictionary of person properties.
- **`group_properties`** (`any`) - A dictionary of group properties.
- **`only_evaluate_locally`** (`bool`) - Whether to only evaluate locally.
- **`send_feature_flag_events`** (`bool`) - Whether to send feature flag events.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP for this request.
- **`device_id?`** (`str`) - The device ID for this request.

### Returns

- `Optional[FeatureFlagResult]`

### Examples

```python
flag_result = posthog.get_feature_flag_result('flag-key', 'distinct_id_of_your_user')
if flag_result and flag_result.get_value() == 'variant-key':
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flag_result.payload
```

---

#### join()

**Release Tag:** public

End the consumer thread once the queue is empty. Do not use directly, call `shutdown()` instead.

### Returns

- `None`

### Examples

```python
posthog.join()
```

---

#### shutdown()

**Release Tag:** public

Flush all messages and cleanly shutdown the client. Call this before the process ends in serverless environments to avoid data loss.

### Returns

- `None`

### Examples

```python
posthog.shutdown()
```

---

### Contexts methods

#### new_context()

**Release Tag:** public

Create a new context for managing shared state. Learn more about [contexts](/docs/libraries/python#contexts).

### Parameters

- **`fresh`** (`bool`) - Whether to create a fresh context that doesn't inherit from parent.
- **`capture_exceptions`** (`bool`) - Whether to automatically capture exceptions in this context.

### Returns

- `None`

### Examples

```python
with posthog.new_context():
    identify_context('<distinct_id>')
    posthog.capture('event_name')
```

---

## PostHog Module Functions

Global functions available in the PostHog module

### Identification methods

#### alias()

**Release Tag:** public

Associate user behaviour before and after they e.g. register, login, or perform some other identifying action.

**Notes:**

To marry up whatever a user does before they sign up or log in with what they do after you need to make an alias call. This will allow you to answer questions like "Which marketing channels leads to users churning after a month?" or "What do users do on our website before signing up?". Particularly useful for associating user behaviour before and after they e.g. register, login, or perform some other identifying action.

### Parameters

- **`previous_id?`** (`any`) - The unique ID of the user before
- **`distinct_id?`** (`any`) - The current unique id
- **`timestamp`** (`any`) - Optional timestamp for the event
- **`uuid`** (`any`) - Optional UUID for the event
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup

### Returns

- `None`

### Examples

```python
# Alias user
from posthog import alias
alias(previous_id='distinct_id', distinct_id='alias_id')
```

---

#### group_identify()

**Release Tag:** public

Set properties on a group.

### Parameters

- **`group_type?`** (`any`) - Type of your group
- **`group_key?`** (`any`) - Unique identifier of the group
- **`properties`** (`any`) - Properties to set on the group
- **`timestamp`** (`any`) - Optional timestamp for the event
- **`uuid`** (`any`) - Optional UUID for the event
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup
- **`distinct_id`** (`any`) - Optional distinct ID of the user performing the action

### Returns

- `None`

### Examples

```python
# Group identify
from posthog import group_identify
group_identify('company', 'company_id_in_your_db', {
    'name': 'Awesome Inc.',
    'employees': 11
})
```

---

#### identify_context()

**Release Tag:** public

Identify the current context with a distinct ID.

### Parameters

- **`distinct_id?`** (`str`) - The distinct ID to associate with the current context and its children

### Returns

- `None`

### Examples

```python
from posthog import identify_context
identify_context("user_123")
```

---

#### set()

**Release Tag:** public

Set properties on a user record.

**Notes:**

This will overwrite previous people property values. Generally operates similar to `capture`, with distinct_id being an optional argument, defaulting to the current context's distinct ID. If there is no context-level distinct ID, and no override distinct_id is passed, this function will do nothing. Context tags are folded into $set properties, so tagging the current context and then calling `set` will cause those tags to be set on the user (unlike capture, which causes them to just be set on the event).

### Parameters

- **`kwargs?`** (`Unpack[OptionalSetArgs]`)

### Returns

- `Optional[str]`

### Examples

```python
# Set person properties
from posthog import capture
capture(
    'distinct_id',
    event='event_name',
    properties={
        '$set': {'name': 'Max Hedgehog'},
        '$set_once': {'initial_url': '/blog'}
    }
)
```

---

#### set_once()

**Release Tag:** public

Set properties on a user record, only if they do not yet exist.

**Notes:**

This will not overwrite previous people property values, unlike `set`. Otherwise, operates in an identical manner to `set`.

### Parameters

- **`kwargs?`** (`Unpack[OptionalSetArgs]`)

### Returns

- `Optional[str]`

### Examples

```python
# Set property once
from posthog import capture
capture(
    'distinct_id',
    event='event_name',
    properties={
        '$set': {'name': 'Max Hedgehog'},
        '$set_once': {'initial_url': '/blog'}
    }
)
```

---

### Events methods

#### capture()

**Release Tag:** public

Capture anything a user does within your system.

**Notes:**

Capture allows you to capture anything a user does within your system, which you can later use in PostHog to find patterns in usage, work out which features to improve or where people are giving up. A capture call requires an event name to specify the event. We recommend using [verb] [noun], like `movie played` or `movie updated` to easily identify what your events mean later on. Capture takes a number of optional arguments, which are defined by the `OptionalCaptureArgs` type.

### Parameters

- **`event?`** (`str`) - The event name to specify the event     **kwargs: Optional arguments including:
- **`kwargs?`** (`Unpack[OptionalCaptureArgs]`)

### Returns

- `Optional[str]`

### Examples

#### Context and capture usage

```python
# Context and capture usage
from posthog import new_context, identify_context, tag_context, capture
# Enter a new context (e.g. a request/response cycle, an instance of a background job, etc)
with new_context():
    # Associate this context with some user, by distinct_id
    identify_context('some user')

    # Capture an event, associated with the context-level distinct ID ('some user')
    capture('movie started')

    # Capture an event associated with some other user (overriding the context-level distinct ID)
    capture('movie joined', distinct_id='some-other-user')

    # Capture an event with some properties
    capture('movie played', properties={'movie_id': '123', 'category': 'romcom'})

    # Capture an event with some properties
    capture('purchase', properties={'product_id': '123', 'category': 'romcom'})
    # Capture an event with some associated group
    capture('purchase', groups={'company': 'id:5'})

    # Adding a tag to the current context will cause it to appear on all subsequent events
    tag_context('some-tag', 'some-value')

    capture('another-event') # Will be captured with `'some-tag': 'some-value'` in the properties dict
```

#### Set event properties

```python
# Set event properties
from posthog import capture
capture(
    "user_signed_up",
    distinct_id="distinct_id_of_the_user",
    properties={
        "login_type": "email",
        "is_free_trial": "true"
    }
)
```

---

#### capture_exception()

**Release Tag:** public

Capture exceptions that happen in your code.

**Notes:**

Capture exception is idempotent - if it is called twice with the same exception instance, only a occurrence will be tracked in posthog. This is because, generally, contexts will cause exceptions to be captured automatically. However, to ensure you track an exception, if you catch and do not re-raise it, capturing it manually is recommended, unless you are certain it will have crossed a context boundary (e.g. by existing a `with posthog.new_context():` block already). If the passed exception was raised and caught, the captured stack trace will consist of every frame between where the exception was raised and the point at which it is captured (the "traceback"). If the passed exception was never raised, e.g. if you call `posthog.capture_exception(ValueError("Some Error"))`, the stack trace captured will be the full stack trace at the moment the exception was captured. Note that heavy use of contexts will lead to truncated stack traces, as the exception will be captured by the context entered most recently, which may not be the point you catch the exception for the final time in your code. It's recommended to use contexts sparingly, for this reason. `capture_exception` takes the same set of optional arguments as `capture`.

### Parameters

- **`exception`** (`BaseException`) - The exception to capture. If not provided, the current exception is captured via `sys.exc_info()`
- **`kwargs?`** (`Unpack[OptionalCaptureArgs]`)

### Returns

- `None`

### Examples

```python
# Capture exception
from posthog import capture_exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e)
```

---

### Feature flags methods

#### evaluate_flags()

**Release Tag:** public

Evaluate all feature flags for a user in a single call and return a :class:`FeatureFlagEvaluations` snapshot. Branch on ``.is_enabled()`` / ``.get_flag()`` and pass the same snapshot to ``capture()`` via the ``flags`` option so events carry the exact flag values the code branched on.  Prefer this over repeated ``get_feature_flag()`` calls and over ``capture(send_feature_flags=True)`` — it consolidates flag evaluation into a single ``/flags`` request per incoming request.

### Parameters

- **`distinct_id`** (`any`) - The user's distinct ID. If ``None``, falls back to the context         distinct_id. If still unresolvable, returns an empty snapshot.
- **`groups`** (`any`) - Mapping of group type to group key.
- **`person_properties`** (`any`) - Person properties to use for evaluation.
- **`group_properties`** (`any`) - Group properties keyed by group type.
- **`only_evaluate_locally`** (`bool`) - If ``True``, never fall back to remote evaluation.
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup.
- **`flag_keys`** (`any`) - Optional list of flag keys. When provided, only these flags are         evaluated — the underlying ``/flags`` request asks the server for just         this subset, which makes the response smaller and the request cheaper.         Use this when you only need a handful of flags out of many.
- **`device_id`** (`any`) - Optional device ID override. If not provided, falls back to the         context device_id (which may be set via tracing headers). Used by         experience-continuity flags to match users across distinct_id changes.

### Returns

- `FeatureFlagEvaluations`

### Examples

```python
from posthog import evaluate_flags, capture
flags = evaluate_flags("user_123", person_properties={"plan": "enterprise"})
if flags.is_enabled("new-dashboard"):
    render_new_dashboard()
capture("page_viewed", distinct_id="user_123", flags=flags)
```

---

#### feature_enabled()

**Release Tag:** public

Use feature flags to enable or disable features for users.

**Notes:**

You can call `posthog.load_feature_flags()` before to make sure you're not doing unexpected requests.

### Parameters

- **`key?`** (`any`) - The feature flag key
- **`distinct_id?`** (`any`) - The user's distinct ID
- **`groups`** (`any`) - Groups mapping
- **`person_properties`** (`any`) - Person properties
- **`group_properties`** (`any`) - Group properties
- **`only_evaluate_locally`** (`bool`) - Whether to evaluate only locally
- **`send_feature_flag_events`** (`bool`) - Whether to send feature flag events
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup
- **`device_id`** (`any`)

### Returns

- `None`

### Examples

```python
# Boolean feature flag
from posthog import feature_enabled, get_feature_flag_payload
is_my_flag_enabled = feature_enabled('flag-key', 'distinct_id_of_your_user')
if is_my_flag_enabled:
    matched_flag_payload = get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
```

---

#### feature_flag_definitions()

**Release Tag:** public

Returns loaded feature flags.

**Notes:**

Returns loaded feature flags, if any. Helpful for debugging what flag information you have loaded.

### Returns

- `None`

### Examples

```python
from posthog import feature_flag_definitions
definitions = feature_flag_definitions()
```

---

#### get_all_flags()

**Release Tag:** public

Get all flags for a given user.

**Notes:**

Flags are key-value pairs where the key is the flag key and the value is the flag variant, or True, or False.

### Parameters

- **`distinct_id?`** (`any`) - The user's distinct ID
- **`groups`** (`any`) - Groups mapping
- **`person_properties`** (`any`) - Person properties
- **`group_properties`** (`any`) - Group properties
- **`only_evaluate_locally`** (`bool`) - Whether to evaluate only locally
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup
- **`device_id`** (`any`)
- **`flag_keys_to_evaluate`** (`any`) - Optional list of flag keys to evaluate (evaluates all if None)

### Returns

- `Optional[dict[str, FeatureFlag]]`

### Examples

```python
# All flags for user
from posthog import get_all_flags
get_all_flags('distinct_id_of_your_user')
```

---

#### get_feature_flag()

**Release Tag:** public

Get feature flag variant for users. Used with experiments.

**Notes:**

`groups` are a mapping from group type to group key. So, if you have a group type of "organization" and a group key of "5", you would pass groups={"organization": "5"}. `group_properties` take the format: { group_type_name: { group_properties } }. So, for example, if you have the group type "organization" and the group key "5", with the properties name, and employee count, you'll send these as: group_properties={"organization": {"name": "PostHog", "employees": 11}}.

### Parameters

- **`key?`** (`any`) - The feature flag key
- **`distinct_id?`** (`any`) - The user's distinct ID
- **`groups`** (`any`) - Groups mapping from group type to group key
- **`person_properties`** (`any`) - Person properties
- **`group_properties`** (`any`) - Group properties in format { group_type_name: { group_properties } }
- **`only_evaluate_locally`** (`bool`) - Whether to evaluate only locally
- **`send_feature_flag_events`** (`bool`) - Whether to send feature flag events
- **`disable_geoip`** (`any`) - Whether to disable GeoIP lookup
- **`device_id`** (`any`)

### Returns

- `Optional[FeatureFlag]`

### Examples

```python
# Multivariate feature flag
from posthog import get_feature_flag, get_feature_flag_payload
enabled_variant = get_feature_flag('flag-key', 'distinct_id_of_your_user')
if enabled_variant == 'variant-key':
    matched_flag_payload = get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
```

---

#### load_feature_flags()

**Release Tag:** public

Load feature flag definitions from PostHog.

### Returns

- `None`

### Examples

```python
from posthog import load_feature_flags
load_feature_flags()
```

---

### Client management methods

#### flush()

**Release Tag:** public

Tell the client to flush all queued events.

### Returns

- `None`

### Examples

```python
from posthog import flush
flush()
```

---

#### join()

**Release Tag:** public

Block program until the client clears the queue. Used during program shutdown. You should use `shutdown()` directly in most cases.

### Returns

- `None`

### Examples

```python
from posthog import join
join()
```

---

#### shutdown()

**Release Tag:** public

Flush all messages and cleanly shutdown the client.

### Returns

- `None`

### Examples

```python
from posthog import shutdown
shutdown()
```

---

### Other methods

#### get_feature_flag_result()

**Release Tag:** public

Get a FeatureFlagResult object which contains the flag result and payload.  This method evaluates a feature flag and returns a FeatureFlagResult object containing: - enabled: Whether the flag is enabled - variant: The variant value if the flag has variants - payload: The payload associated with the flag (automatically deserialized from JSON) - key: The flag key - reason: Why the flag was enabled/disabled  Example: ```python result = posthog.get_feature_flag_result('beta-feature', 'distinct_id') if result and result.enabled:     # Use the variant and payload     print(f"Variant: {result.variant}")     print(f"Payload: {result.payload}") ```

### Parameters

- **`key?`** (`any`)
- **`distinct_id?`** (`any`)
- **`groups`** (`any`)
- **`person_properties`** (`any`)
- **`group_properties`** (`any`)
- **`only_evaluate_locally`** (`bool`)
- **`send_feature_flag_events`** (`bool`)
- **`disable_geoip`** (`any`)
- **`device_id`** (`any`)

### Returns

- `None`

---

#### get_remote_config_payload()

**Release Tag:** public

Get the payload for a remote config feature flag.

### Parameters

- **`key?`** (`any`) - The key of the feature flag

### Returns

- `None`

---

#### set_capture_exception_code_variables_context()

**Release Tag:** public

Set whether code variables are captured for the current context.

### Parameters

- **`enabled?`** (`bool`)

### Returns

- `None`

---

#### set_code_variables_ignore_patterns_context()

**Release Tag:** public

Variable names matching these patterns will be ignored completely when capturing code variables.

### Parameters

- **`ignore_patterns?`** (`list`)

### Returns

- `None`

---

#### set_code_variables_mask_patterns_context()

**Release Tag:** public

Variable names matching these patterns will be masked with *** when capturing code variables.

### Parameters

- **`mask_patterns?`** (`list`)

### Returns

- `None`

---

### Contexts methods

#### get_tags()

**Release Tag:** public

Get all tags from the current context.  Returns:     Dict of all tags in the current context

### Returns

- `dict[str, Any]`

---

#### new_context()

**Release Tag:** public

Create a new context scope that will be active for the duration of the with block.

### Parameters

- **`fresh`** (`bool`) - Whether to start with a fresh context (default: False)
- **`capture_exceptions`** (`bool`) - Whether to capture exceptions raised within the context (default: True)
- **`client`** (`any`) - Optional Posthog client instance to use for this context (default: None)

### Returns

- `None`

### Examples

```python
from posthog import new_context, tag, capture
with new_context():
    tag("request_id", "123")
    capture("event_name", properties={"property": "value"})
```

---

#### scoped()

**Release Tag:** public

Decorator that creates a new context for the function.

### Parameters

- **`fresh`** (`bool`) - Whether to start with a fresh context (default: False)
- **`capture_exceptions`** (`bool`) - Whether to capture and track exceptions with posthog error tracking (default: True)

### Returns

- `None`

### Examples

```python
from posthog import scoped, tag, capture
@scoped()
def process_payment(payment_id):
    tag("payment_id", payment_id)
    capture("payment_started")
```

---

#### set_context_device_id()

**Release Tag:** public

Set the device ID for the current context, associating all feature flag requests in this or child contexts with the given device ID.

### Parameters

- **`device_id?`** (`str`) - The device ID to associate with the current context and its children

### Returns

- `None`

### Examples

```python
from posthog import set_context_device_id
set_context_device_id("device_123")
```

---

#### set_context_session()

**Release Tag:** public

Set the session ID for the current context.

### Parameters

- **`session_id?`** (`str`) - The session ID to associate with the current context and its children

### Returns

- `None`

### Examples

```python
from posthog import set_context_session
set_context_session("session_123")
```

---

#### tag()

**Release Tag:** public

Add a tag to the current context.

### Parameters

- **`name?`** (`str`) - The tag key
- **`value?`** (`Any`) - The tag value

### Returns

- `None`

### Examples

```python
from posthog import tag
tag("user_id", "123")
```

---