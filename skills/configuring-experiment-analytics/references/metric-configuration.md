# Metric configuration

All metrics use `kind: "ExperimentMetric"`. Legacy kinds (`ExperimentTrendsQuery`, `ExperimentFunnelsQuery`) are rejected.

The full Pydantic schema below is rendered from `posthog/schema.py` at build
time — if a field is missing here, fix the model. It is the `ExperimentMetric`
discriminated union: pick the variant matching your `metric_type` (`mean`,
`funnel`, `ratio`, `retention`) under `$defs`, and read that variant's
`required` array for the mandatory fields. The shared event-source building
blocks (`EventsNode`, `ActionsNode`, `ExperimentDataWarehouseNode`) and the
property-filter types are defined once under `$defs` and referenced by `$ref`.
The schema is authoritative; the prose and examples below are guidance.

## Schema

```json
{
  "$defs": {
    "ActionsNode": {
      "additionalProperties": false,
      "properties": {
        "custom_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Custom Name"
        },
        "fixedProperties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Fixed properties in the query, can't be edited in the interface (e.g. scoping down by person)",
          "title": "Fixedproperties"
        },
        "id": {
          "title": "Id",
          "type": "integer"
        },
        "kind": {
          "const": "ActionsNode",
          "default": "ActionsNode",
          "title": "Kind",
          "type": "string"
        },
        "math": {
          "anyOf": [
            {
              "$ref": "#/$defs/BaseMathType"
            },
            {
              "$ref": "#/$defs/FunnelMathType"
            },
            {
              "$ref": "#/$defs/PropertyMathType"
            },
            {
              "$ref": "#/$defs/CountPerActorMathType"
            },
            {
              "$ref": "#/$defs/ExperimentMetricMathType"
            },
            {
              "$ref": "#/$defs/CalendarHeatmapMathType"
            },
            {
              "const": "unique_group",
              "type": "string"
            },
            {
              "const": "hogql",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math"
        },
        "math_group_type_index": {
          "anyOf": [
            {
              "$ref": "#/$defs/MathGroupTypeIndex"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_hogql": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Hogql"
        },
        "math_multiplier": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Multiplier"
        },
        "math_property": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property"
        },
        "math_property_revenue_currency": {
          "anyOf": [
            {
              "$ref": "#/$defs/RevenueCurrencyPropertyConfig"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_property_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property Type"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "optionalInFunnel": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Optionalinfunnel"
        },
        "properties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Properties configurable in the interface",
          "title": "Properties"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "id"
      ],
      "title": "ActionsNode",
      "type": "object"
    },
    "BaseMathType": {
      "enum": [
        "total",
        "dau",
        "weekly_active",
        "monthly_active",
        "unique_session",
        "first_time_for_user",
        "first_matching_event_for_user"
      ],
      "title": "BaseMathType",
      "type": "string"
    },
    "Breakdown": {
      "additionalProperties": false,
      "properties": {
        "group_type_index": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Group Type Index"
        },
        "histogram_bin_count": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Histogram Bin Count"
        },
        "normalize_url": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Normalize Url"
        },
        "property": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "integer"
            }
          ],
          "title": "Property"
        },
        "type": {
          "anyOf": [
            {
              "$ref": "#/$defs/MultipleBreakdownType"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "required": [
        "property"
      ],
      "title": "Breakdown",
      "type": "object"
    },
    "BreakdownFilter": {
      "additionalProperties": false,
      "properties": {
        "breakdown": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "integer"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown"
        },
        "breakdown_group_type_index": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Group Type Index"
        },
        "breakdown_hide_other_aggregation": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Hide Other Aggregation"
        },
        "breakdown_histogram_bin_count": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Histogram Bin Count"
        },
        "breakdown_limit": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Limit"
        },
        "breakdown_normalize_url": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Normalize Url"
        },
        "breakdown_path_cleaning": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdown Path Cleaning"
        },
        "breakdown_type": {
          "anyOf": [
            {
              "$ref": "#/$defs/BreakdownType"
            },
            {
              "type": "null"
            }
          ],
          "default": "event"
        },
        "breakdowns": {
          "anyOf": [
            {
              "items": {
                "$ref": "#/$defs/Breakdown"
              },
              "maxItems": 3,
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Breakdowns"
        }
      },
      "title": "BreakdownFilter",
      "type": "object"
    },
    "BreakdownType": {
      "enum": [
        "cohort",
        "person",
        "event",
        "event_metadata",
        "group",
        "session",
        "hogql",
        "data_warehouse",
        "data_warehouse_person_property",
        "revenue_analytics"
      ],
      "title": "BreakdownType",
      "type": "string"
    },
    "CalendarHeatmapMathType": {
      "enum": [
        "total",
        "dau"
      ],
      "title": "CalendarHeatmapMathType",
      "type": "string"
    },
    "CohortPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "cohort_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Cohort Name"
        },
        "key": {
          "const": "id",
          "default": "id",
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "anyOf": [
            {
              "$ref": "#/$defs/PropertyOperator"
            },
            {
              "type": "null"
            }
          ],
          "default": "in"
        },
        "type": {
          "const": "cohort",
          "default": "cohort",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "title": "Value",
          "type": "integer"
        }
      },
      "required": [
        "value"
      ],
      "title": "CohortPropertyFilter",
      "type": "object"
    },
    "CountPerActorMathType": {
      "enum": [
        "avg_count_per_actor",
        "min_count_per_actor",
        "max_count_per_actor",
        "median_count_per_actor",
        "p75_count_per_actor",
        "p90_count_per_actor",
        "p95_count_per_actor",
        "p99_count_per_actor"
      ],
      "title": "CountPerActorMathType",
      "type": "string"
    },
    "CurrencyCode": {
      "enum": [
        "AED",
        "AFN",
        "ALL",
        "AMD",
        "ANG",
        "AOA",
        "ARS",
        "AUD",
        "AWG",
        "AZN",
        "BAM",
        "BBD",
        "BDT",
        "BGN",
        "BHD",
        "BIF",
        "BMD",
        "BND",
        "BOB",
        "BRL",
        "BSD",
        "BTC",
        "BTN",
        "BWP",
        "BYN",
        "BZD",
        "CAD",
        "CDF",
        "CHF",
        "CLP",
        "CNY",
        "COP",
        "CRC",
        "CVE",
        "CZK",
        "DJF",
        "DKK",
        "DOP",
        "DZD",
        "EGP",
        "ERN",
        "ETB",
        "EUR",
        "FJD",
        "GBP",
        "GEL",
        "GHS",
        "GIP",
        "GMD",
        "GNF",
        "GTQ",
        "GYD",
        "HKD",
        "HNL",
        "HRK",
        "HTG",
        "HUF",
        "IDR",
        "ILS",
        "INR",
        "IQD",
        "IRR",
        "ISK",
        "JMD",
        "JOD",
        "JPY",
        "KES",
        "KGS",
        "KHR",
        "KMF",
        "KRW",
        "KWD",
        "KYD",
        "KZT",
        "LAK",
        "LBP",
        "LKR",
        "LRD",
        "LTL",
        "LVL",
        "LSL",
        "LYD",
        "MAD",
        "MDL",
        "MGA",
        "MKD",
        "MMK",
        "MNT",
        "MOP",
        "MRU",
        "MTL",
        "MUR",
        "MVR",
        "MWK",
        "MXN",
        "MYR",
        "MZN",
        "NAD",
        "NGN",
        "NIO",
        "NOK",
        "NPR",
        "NZD",
        "OMR",
        "PAB",
        "PEN",
        "PGK",
        "PHP",
        "PKR",
        "PLN",
        "PYG",
        "QAR",
        "RON",
        "RSD",
        "RUB",
        "RWF",
        "SAR",
        "SBD",
        "SCR",
        "SDG",
        "SEK",
        "SGD",
        "SRD",
        "SSP",
        "STN",
        "SYP",
        "SZL",
        "THB",
        "TJS",
        "TMT",
        "TND",
        "TOP",
        "TRY",
        "TTD",
        "TWD",
        "TZS",
        "UAH",
        "UGX",
        "USD",
        "UYU",
        "UZS",
        "VES",
        "VND",
        "VUV",
        "WST",
        "XAF",
        "XCD",
        "XOF",
        "XPF",
        "YER",
        "ZAR",
        "ZMW"
      ],
      "title": "CurrencyCode",
      "type": "string"
    },
    "DataWarehousePersonPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "data_warehouse_person_property",
          "default": "data_warehouse_person_property",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "DataWarehousePersonPropertyFilter",
      "type": "object"
    },
    "DataWarehousePropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "data_warehouse",
          "default": "data_warehouse",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "DataWarehousePropertyFilter",
      "type": "object"
    },
    "DurationType": {
      "enum": [
        "duration",
        "active_seconds",
        "inactive_seconds"
      ],
      "title": "DurationType",
      "type": "string"
    },
    "ElementPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "$ref": "#/$defs/Key10"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "element",
          "default": "element",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "ElementPropertyFilter",
      "type": "object"
    },
    "EmptyPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "type": {
          "const": "empty",
          "default": "empty",
          "title": "Type",
          "type": "string"
        }
      },
      "title": "EmptyPropertyFilter",
      "type": "object"
    },
    "ErrorTrackingIssueFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "error_tracking_issue",
          "default": "error_tracking_issue",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "ErrorTrackingIssueFilter",
      "type": "object"
    },
    "EventMetadataPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "event_metadata",
          "default": "event_metadata",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "EventMetadataPropertyFilter",
      "type": "object"
    },
    "EventPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "anyOf": [
            {
              "$ref": "#/$defs/PropertyOperator"
            },
            {
              "type": "null"
            }
          ],
          "default": "exact"
        },
        "type": {
          "const": "event",
          "default": "event",
          "description": "Event properties",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key"
      ],
      "title": "EventPropertyFilter",
      "type": "object"
    },
    "EventsNode": {
      "additionalProperties": false,
      "properties": {
        "custom_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Custom Name"
        },
        "event": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "The event or `null` for all events.",
          "title": "Event"
        },
        "fixedProperties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Fixed properties in the query, can't be edited in the interface (e.g. scoping down by person)",
          "title": "Fixedproperties"
        },
        "kind": {
          "const": "EventsNode",
          "default": "EventsNode",
          "title": "Kind",
          "type": "string"
        },
        "limit": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Limit"
        },
        "math": {
          "anyOf": [
            {
              "$ref": "#/$defs/BaseMathType"
            },
            {
              "$ref": "#/$defs/FunnelMathType"
            },
            {
              "$ref": "#/$defs/PropertyMathType"
            },
            {
              "$ref": "#/$defs/CountPerActorMathType"
            },
            {
              "$ref": "#/$defs/ExperimentMetricMathType"
            },
            {
              "$ref": "#/$defs/CalendarHeatmapMathType"
            },
            {
              "const": "unique_group",
              "type": "string"
            },
            {
              "const": "hogql",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math"
        },
        "math_group_type_index": {
          "anyOf": [
            {
              "$ref": "#/$defs/MathGroupTypeIndex"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_hogql": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Hogql"
        },
        "math_multiplier": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Multiplier"
        },
        "math_property": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property"
        },
        "math_property_revenue_currency": {
          "anyOf": [
            {
              "$ref": "#/$defs/RevenueCurrencyPropertyConfig"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_property_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property Type"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "optionalInFunnel": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Optionalinfunnel"
        },
        "orderBy": {
          "anyOf": [
            {
              "items": {
                "type": "string"
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Columns to order by",
          "title": "Orderby"
        },
        "properties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Properties configurable in the interface",
          "title": "Properties"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "title": "EventsNode",
      "type": "object"
    },
    "ExperimentDataWarehouseNode": {
      "additionalProperties": false,
      "properties": {
        "custom_name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Custom Name"
        },
        "data_warehouse_join_key": {
          "title": "Data Warehouse Join Key",
          "type": "string"
        },
        "events_join_key": {
          "title": "Events Join Key",
          "type": "string"
        },
        "fixedProperties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Fixed properties in the query, can't be edited in the interface (e.g. scoping down by person)",
          "title": "Fixedproperties"
        },
        "kind": {
          "const": "ExperimentDataWarehouseNode",
          "default": "ExperimentDataWarehouseNode",
          "title": "Kind",
          "type": "string"
        },
        "math": {
          "anyOf": [
            {
              "$ref": "#/$defs/BaseMathType"
            },
            {
              "$ref": "#/$defs/FunnelMathType"
            },
            {
              "$ref": "#/$defs/PropertyMathType"
            },
            {
              "$ref": "#/$defs/CountPerActorMathType"
            },
            {
              "$ref": "#/$defs/ExperimentMetricMathType"
            },
            {
              "$ref": "#/$defs/CalendarHeatmapMathType"
            },
            {
              "const": "unique_group",
              "type": "string"
            },
            {
              "const": "hogql",
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math"
        },
        "math_group_type_index": {
          "anyOf": [
            {
              "$ref": "#/$defs/MathGroupTypeIndex"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_hogql": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Hogql"
        },
        "math_multiplier": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Multiplier"
        },
        "math_property": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property"
        },
        "math_property_revenue_currency": {
          "anyOf": [
            {
              "$ref": "#/$defs/RevenueCurrencyPropertyConfig"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "math_property_type": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Math Property Type"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "optionalInFunnel": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Optionalinfunnel"
        },
        "properties": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "$ref": "#/$defs/EventPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/PersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ElementPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EventMetadataPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SessionPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/CohortPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RecordingPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/LogEntryPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/GroupPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FeaturePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/FlagPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/HogQLPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/EmptyPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/DataWarehousePersonPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/ErrorTrackingIssueFilter"
                  },
                  {
                    "$ref": "#/$defs/LogPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/SpanPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/RevenueAnalyticsPropertyFilter"
                  },
                  {
                    "$ref": "#/$defs/WorkflowVariablePropertyFilter"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Properties configurable in the interface",
          "title": "Properties"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "table_name": {
          "title": "Table Name",
          "type": "string"
        },
        "timestamp_field": {
          "title": "Timestamp Field",
          "type": "string"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "data_warehouse_join_key",
        "events_join_key",
        "table_name",
        "timestamp_field"
      ],
      "title": "ExperimentDataWarehouseNode",
      "type": "object"
    },
    "ExperimentFunnelMetric": {
      "additionalProperties": false,
      "properties": {
        "breakdownFilter": {
          "anyOf": [
            {
              "$ref": "#/$defs/BreakdownFilter"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "conversion_window": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Conversion Window"
        },
        "conversion_window_unit": {
          "anyOf": [
            {
              "$ref": "#/$defs/FunnelConversionWindowTimeUnit"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "fingerprint": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Fingerprint"
        },
        "funnel_order_type": {
          "anyOf": [
            {
              "$ref": "#/$defs/StepOrderValue"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricGoal"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "isSharedMetric": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Issharedmetric"
        },
        "kind": {
          "const": "ExperimentMetric",
          "default": "ExperimentMetric",
          "title": "Kind",
          "type": "string"
        },
        "metric_type": {
          "const": "funnel",
          "default": "funnel",
          "title": "Metric Type",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "series": {
          "items": {
            "discriminator": {
              "mapping": {
                "ActionsNode": "#/$defs/ActionsNode",
                "EventsNode": "#/$defs/EventsNode",
                "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
              },
              "propertyName": "kind"
            },
            "oneOf": [
              {
                "$ref": "#/$defs/EventsNode"
              },
              {
                "$ref": "#/$defs/ActionsNode"
              },
              {
                "$ref": "#/$defs/ExperimentDataWarehouseNode"
              }
            ]
          },
          "title": "Series",
          "type": "array"
        },
        "sharedMetricId": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Sharedmetricid"
        },
        "uuid": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Uuid"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "series"
      ],
      "title": "ExperimentFunnelMetric",
      "type": "object"
    },
    "ExperimentMeanMetric": {
      "additionalProperties": false,
      "properties": {
        "breakdownFilter": {
          "anyOf": [
            {
              "$ref": "#/$defs/BreakdownFilter"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "conversion_window": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Conversion Window"
        },
        "conversion_window_unit": {
          "anyOf": [
            {
              "$ref": "#/$defs/FunnelConversionWindowTimeUnit"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "fingerprint": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Fingerprint"
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricGoal"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "ignore_zeros": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Ignore Zeros"
        },
        "isSharedMetric": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Issharedmetric"
        },
        "kind": {
          "const": "ExperimentMetric",
          "default": "ExperimentMetric",
          "title": "Kind",
          "type": "string"
        },
        "lower_bound_percentile": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Winsorization lower percentile bound, as a fraction in [0, 1] (e.g. 0.01 for the 1st percentile).",
          "title": "Lower Bound Percentile"
        },
        "metric_type": {
          "const": "mean",
          "default": "mean",
          "title": "Metric Type",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "sharedMetricId": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Sharedmetricid"
        },
        "source": {
          "discriminator": {
            "mapping": {
              "ActionsNode": "#/$defs/ActionsNode",
              "EventsNode": "#/$defs/EventsNode",
              "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
            },
            "propertyName": "kind"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/EventsNode"
            },
            {
              "$ref": "#/$defs/ActionsNode"
            },
            {
              "$ref": "#/$defs/ExperimentDataWarehouseNode"
            }
          ],
          "title": "Source"
        },
        "upper_bound_percentile": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Winsorization upper percentile bound, as a fraction in [0, 1] (e.g. 0.99 for the 99th percentile).",
          "title": "Upper Bound Percentile"
        },
        "uuid": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Uuid"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "source"
      ],
      "title": "ExperimentMeanMetric",
      "type": "object"
    },
    "ExperimentMetricGoal": {
      "enum": [
        "increase",
        "decrease"
      ],
      "title": "ExperimentMetricGoal",
      "type": "string"
    },
    "ExperimentMetricMathType": {
      "enum": [
        "total",
        "sum",
        "unique_session",
        "min",
        "max",
        "avg",
        "dau",
        "unique_group",
        "hogql"
      ],
      "title": "ExperimentMetricMathType",
      "type": "string"
    },
    "ExperimentMetricOutlierHandling": {
      "additionalProperties": false,
      "properties": {
        "ignore_zeros": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Ignore Zeros"
        },
        "lower_bound_percentile": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Winsorization lower percentile bound, as a fraction in [0, 1] (e.g. 0.01 for the 1st percentile).",
          "title": "Lower Bound Percentile"
        },
        "upper_bound_percentile": {
          "anyOf": [
            {
              "maximum": 1.0,
              "minimum": 0.0,
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "Winsorization upper percentile bound, as a fraction in [0, 1] (e.g. 0.99 for the 99th percentile).",
          "title": "Upper Bound Percentile"
        }
      },
      "title": "ExperimentMetricOutlierHandling",
      "type": "object"
    },
    "ExperimentRatioMetric": {
      "additionalProperties": false,
      "properties": {
        "breakdownFilter": {
          "anyOf": [
            {
              "$ref": "#/$defs/BreakdownFilter"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "conversion_window": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Conversion Window"
        },
        "conversion_window_unit": {
          "anyOf": [
            {
              "$ref": "#/$defs/FunnelConversionWindowTimeUnit"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "denominator": {
          "discriminator": {
            "mapping": {
              "ActionsNode": "#/$defs/ActionsNode",
              "EventsNode": "#/$defs/EventsNode",
              "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
            },
            "propertyName": "kind"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/EventsNode"
            },
            {
              "$ref": "#/$defs/ActionsNode"
            },
            {
              "$ref": "#/$defs/ExperimentDataWarehouseNode"
            }
          ],
          "title": "Denominator"
        },
        "denominator_outlier_handling": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricOutlierHandling"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "fingerprint": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Fingerprint"
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricGoal"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "isSharedMetric": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Issharedmetric"
        },
        "kind": {
          "const": "ExperimentMetric",
          "default": "ExperimentMetric",
          "title": "Kind",
          "type": "string"
        },
        "metric_type": {
          "const": "ratio",
          "default": "ratio",
          "title": "Metric Type",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "numerator": {
          "discriminator": {
            "mapping": {
              "ActionsNode": "#/$defs/ActionsNode",
              "EventsNode": "#/$defs/EventsNode",
              "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
            },
            "propertyName": "kind"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/EventsNode"
            },
            {
              "$ref": "#/$defs/ActionsNode"
            },
            {
              "$ref": "#/$defs/ExperimentDataWarehouseNode"
            }
          ],
          "title": "Numerator"
        },
        "numerator_outlier_handling": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricOutlierHandling"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "sharedMetricId": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Sharedmetricid"
        },
        "uuid": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Uuid"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "denominator",
        "numerator"
      ],
      "title": "ExperimentRatioMetric",
      "type": "object"
    },
    "ExperimentRetentionMetric": {
      "additionalProperties": false,
      "properties": {
        "breakdownFilter": {
          "anyOf": [
            {
              "$ref": "#/$defs/BreakdownFilter"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "completion_event": {
          "discriminator": {
            "mapping": {
              "ActionsNode": "#/$defs/ActionsNode",
              "EventsNode": "#/$defs/EventsNode",
              "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
            },
            "propertyName": "kind"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/EventsNode"
            },
            {
              "$ref": "#/$defs/ActionsNode"
            },
            {
              "$ref": "#/$defs/ExperimentDataWarehouseNode"
            }
          ],
          "title": "Completion Event"
        },
        "conversion_window": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Conversion Window"
        },
        "conversion_window_unit": {
          "anyOf": [
            {
              "$ref": "#/$defs/FunnelConversionWindowTimeUnit"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "fingerprint": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Fingerprint"
        },
        "goal": {
          "anyOf": [
            {
              "$ref": "#/$defs/ExperimentMetricGoal"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        },
        "isSharedMetric": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Issharedmetric"
        },
        "kind": {
          "const": "ExperimentMetric",
          "default": "ExperimentMetric",
          "title": "Kind",
          "type": "string"
        },
        "metric_type": {
          "const": "retention",
          "default": "retention",
          "title": "Metric Type",
          "type": "string"
        },
        "name": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Name"
        },
        "response": {
          "anyOf": [
            {
              "additionalProperties": true,
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Response"
        },
        "retention_window_end": {
          "title": "Retention Window End",
          "type": "integer"
        },
        "retention_window_start": {
          "title": "Retention Window Start",
          "type": "integer"
        },
        "retention_window_unit": {
          "$ref": "#/$defs/FunnelConversionWindowTimeUnit"
        },
        "sharedMetricId": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Sharedmetricid"
        },
        "start_event": {
          "discriminator": {
            "mapping": {
              "ActionsNode": "#/$defs/ActionsNode",
              "EventsNode": "#/$defs/EventsNode",
              "ExperimentDataWarehouseNode": "#/$defs/ExperimentDataWarehouseNode"
            },
            "propertyName": "kind"
          },
          "oneOf": [
            {
              "$ref": "#/$defs/EventsNode"
            },
            {
              "$ref": "#/$defs/ActionsNode"
            },
            {
              "$ref": "#/$defs/ExperimentDataWarehouseNode"
            }
          ],
          "title": "Start Event"
        },
        "start_handling": {
          "$ref": "#/$defs/StartHandling"
        },
        "uuid": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Uuid"
        },
        "version": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "description": "version of the node, used for schema migrations",
          "title": "Version"
        }
      },
      "required": [
        "completion_event",
        "retention_window_end",
        "retention_window_start",
        "retention_window_unit",
        "start_event",
        "start_handling"
      ],
      "title": "ExperimentRetentionMetric",
      "type": "object"
    },
    "FeaturePropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "feature",
          "default": "feature",
          "description": "Event property with \"$feature/\" prepended",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "FeaturePropertyFilter",
      "type": "object"
    },
    "FlagPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "description": "The key should be the flag ID",
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "const": "flag_evaluates_to",
          "default": "flag_evaluates_to",
          "description": "Only flag_evaluates_to operator is allowed for flag dependencies",
          "title": "Operator",
          "type": "string"
        },
        "type": {
          "const": "flag",
          "default": "flag",
          "description": "Feature flag dependency",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "type": "boolean"
            },
            {
              "type": "string"
            }
          ],
          "description": "The value can be true, false, or a variant name",
          "title": "Value"
        }
      },
      "required": [
        "key",
        "value"
      ],
      "title": "FlagPropertyFilter",
      "type": "object"
    },
    "FunnelConversionWindowTimeUnit": {
      "enum": [
        "second",
        "minute",
        "hour",
        "day",
        "week",
        "month"
      ],
      "title": "FunnelConversionWindowTimeUnit",
      "type": "string"
    },
    "FunnelMathType": {
      "enum": [
        "total",
        "first_time_for_user",
        "first_time_for_user_with_filters"
      ],
      "title": "FunnelMathType",
      "type": "string"
    },
    "GroupPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "group_key_names": {
          "anyOf": [
            {
              "additionalProperties": {
                "type": "string"
              },
              "type": "object"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Group Key Names"
        },
        "group_type_index": {
          "anyOf": [
            {
              "type": "integer"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Group Type Index"
        },
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "group",
          "default": "group",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "GroupPropertyFilter",
      "type": "object"
    },
    "HogQLPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "type": {
          "const": "hogql",
          "default": "hogql",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key"
      ],
      "title": "HogQLPropertyFilter",
      "type": "object"
    },
    "Key10": {
      "enum": [
        "tag_name",
        "text",
        "href",
        "selector"
      ],
      "title": "Key10",
      "type": "string"
    },
    "LogEntryPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "log_entry",
          "default": "log_entry",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "LogEntryPropertyFilter",
      "type": "object"
    },
    "LogPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "$ref": "#/$defs/LogPropertyFilterType"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator",
        "type"
      ],
      "title": "LogPropertyFilter",
      "type": "object"
    },
    "LogPropertyFilterType": {
      "enum": [
        "log",
        "log_attribute",
        "log_resource_attribute"
      ],
      "title": "LogPropertyFilterType",
      "type": "string"
    },
    "MathGroupTypeIndex": {
      "enum": [
        0.0,
        1.0,
        2.0,
        3.0,
        4.0
      ],
      "title": "MathGroupTypeIndex",
      "type": "number"
    },
    "MultipleBreakdownType": {
      "enum": [
        "person",
        "event",
        "event_metadata",
        "group",
        "session",
        "hogql",
        "cohort",
        "revenue_analytics",
        "data_warehouse",
        "data_warehouse_person_property"
      ],
      "title": "MultipleBreakdownType",
      "type": "string"
    },
    "PersonPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "person",
          "default": "person",
          "description": "Person properties",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "PersonPropertyFilter",
      "type": "object"
    },
    "PropertyMathType": {
      "enum": [
        "avg",
        "sum",
        "min",
        "max",
        "median",
        "p75",
        "p90",
        "p95",
        "p99"
      ],
      "title": "PropertyMathType",
      "type": "string"
    },
    "PropertyOperator": {
      "enum": [
        "exact",
        "is_not",
        "icontains",
        "not_icontains",
        "regex",
        "not_regex",
        "gt",
        "gte",
        "lt",
        "lte",
        "is_set",
        "is_not_set",
        "is_date_exact",
        "is_date_before",
        "is_date_after",
        "between",
        "not_between",
        "min",
        "max",
        "in",
        "not_in",
        "is_cleaned_path_exact",
        "flag_evaluates_to",
        "semver_eq",
        "semver_neq",
        "semver_gt",
        "semver_gte",
        "semver_lt",
        "semver_lte",
        "semver_tilde",
        "semver_caret",
        "semver_wildcard",
        "icontains_multi",
        "not_icontains_multi"
      ],
      "title": "PropertyOperator",
      "type": "string"
    },
    "RecordingPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "anyOf": [
            {
              "$ref": "#/$defs/DurationType"
            },
            {
              "type": "string"
            }
          ],
          "title": "Key"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "recording",
          "default": "recording",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "RecordingPropertyFilter",
      "type": "object"
    },
    "RevenueAnalyticsPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "revenue_analytics",
          "default": "revenue_analytics",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "RevenueAnalyticsPropertyFilter",
      "type": "object"
    },
    "RevenueCurrencyPropertyConfig": {
      "additionalProperties": false,
      "properties": {
        "property": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Property"
        },
        "static": {
          "anyOf": [
            {
              "$ref": "#/$defs/CurrencyCode"
            },
            {
              "type": "null"
            }
          ],
          "default": null
        }
      },
      "title": "RevenueCurrencyPropertyConfig",
      "type": "object"
    },
    "SessionPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "session",
          "default": "session",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "SessionPropertyFilter",
      "type": "object"
    },
    "SpanPropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "$ref": "#/$defs/SpanPropertyFilterType"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator",
        "type"
      ],
      "title": "SpanPropertyFilter",
      "type": "object"
    },
    "SpanPropertyFilterType": {
      "enum": [
        "span",
        "span_attribute",
        "span_resource_attribute"
      ],
      "title": "SpanPropertyFilterType",
      "type": "string"
    },
    "StartHandling": {
      "enum": [
        "first_seen",
        "last_seen"
      ],
      "title": "StartHandling",
      "type": "string"
    },
    "StepOrderValue": {
      "enum": [
        "strict",
        "unordered",
        "ordered"
      ],
      "title": "StepOrderValue",
      "type": "string"
    },
    "WorkflowVariablePropertyFilter": {
      "additionalProperties": false,
      "properties": {
        "key": {
          "title": "Key",
          "type": "string"
        },
        "label": {
          "anyOf": [
            {
              "type": "string"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Label"
        },
        "operator": {
          "$ref": "#/$defs/PropertyOperator"
        },
        "type": {
          "const": "workflow_variable",
          "default": "workflow_variable",
          "title": "Type",
          "type": "string"
        },
        "value": {
          "anyOf": [
            {
              "items": {
                "anyOf": [
                  {
                    "type": "string"
                  },
                  {
                    "type": "number"
                  },
                  {
                    "type": "boolean"
                  }
                ]
              },
              "type": "array"
            },
            {
              "type": "string"
            },
            {
              "type": "number"
            },
            {
              "type": "boolean"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Value"
        }
      },
      "required": [
        "key",
        "operator"
      ],
      "title": "WorkflowVariablePropertyFilter",
      "type": "object"
    }
  },
  "discriminator": {
    "mapping": {
      "funnel": "#/$defs/ExperimentFunnelMetric",
      "mean": "#/$defs/ExperimentMeanMetric",
      "ratio": "#/$defs/ExperimentRatioMetric",
      "retention": "#/$defs/ExperimentRetentionMetric"
    },
    "propertyName": "metric_type"
  },
  "oneOf": [
    {
      "$ref": "#/$defs/ExperimentMeanMetric"
    },
    {
      "$ref": "#/$defs/ExperimentFunnelMetric"
    },
    {
      "$ref": "#/$defs/ExperimentRatioMetric"
    },
    {
      "$ref": "#/$defs/ExperimentRetentionMetric"
    }
  ],
  "title": "ExperimentMetric"
}
```

## Mean metric

Average of a numeric property per user. Use for revenue per user, session
duration, page views per user, and similar magnitudes. Drives the math via the
`source.math` / `source.math_property` pair on a single `EventsNode`,
`ActionsNode`, or `ExperimentDataWarehouseNode`.

### Right

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "mean",
  "name": "Average revenue per user",
  "source": {
    "kind": "EventsNode",
    "event": "purchase_completed",
    "math": "sum",
    "math_property": "revenue"
  }
}
```

## Funnel metric

Conversion rate from exposure through one or more ordered actions. The
experiment's exposure event is automatically prepended as `step_0`, so even a
single entry in `series` creates a valid 2-step funnel (exposure → action).

### Right — single-step funnel (exposure → action)

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "funnel",
  "name": "Reached checkout",
  "series": [{ "kind": "EventsNode", "event": "checkout_started" }]
}
```

Measures "% of exposed users who reached checkout".

### Right — multi-step funnel (exposure → action 1 → action 2 → ...)

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "funnel",
  "name": "Checkout conversion",
  "series": [
    { "kind": "EventsNode", "event": "add_to_cart" },
    { "kind": "EventsNode", "event": "checkout_started" },
    { "kind": "EventsNode", "event": "purchase_completed" }
  ]
}
```

Step order matters — users must complete steps in sequence.

## Ratio metric

Rate of one event relative to another. Each side (`numerator`, `denominator`)
is an `EventsNode` / `ActionsNode` / `ExperimentDataWarehouseNode` with its own
`math` and `math_property` — the math determines how each side is aggregated
before the ratio is taken.

Use for revenue per pageview, click-through rate, error rate, engagement
ratios.

### Right — click-through rate (count / count)

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "ratio",
  "name": "Click-through rate",
  "numerator": {
    "kind": "EventsNode",
    "event": "button_clicked"
  },
  "denominator": {
    "kind": "EventsNode",
    "event": "$pageview"
  }
}
```

### Right — revenue per pageview (sum of property / count)

To divide a property sum by an event count, the numerator's `math` is `"sum"`
and `math_property` names the numeric property to sum. The denominator stays
at the default count.

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "ratio",
  "name": "Revenue per pageview",
  "numerator": {
    "kind": "EventsNode",
    "event": "purchase_completed",
    "math": "sum",
    "math_property": "revenue"
  },
  "denominator": {
    "kind": "EventsNode",
    "event": "$pageview"
  }
}
```

### Wrong — `is_set` filter instead of `math` / `math_property`

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "ratio",
  "name": "Revenue per pageview",
  "numerator": {
    "kind": "EventsNode",
    "event": "purchase_completed",
    "properties": [
      { "key": "revenue", "value": "is_set", "operator": "is_set", "type": "event" }
    ]
  },
  "denominator": { "kind": "EventsNode", "event": "$pageview" }
}
```

A property filter scopes *which events* count — it does not sum them. The
numerator above counts purchases that have a revenue property, not the revenue
total. Aggregation lives in `math` / `math_property`, never in a filter.

## Retention metric

Whether users return after initial exposure. Tracks `start_event` →
`completion_event` over a window defined by `retention_window_start`,
`retention_window_end`, and `retention_window_unit`. `start_handling` is
required and controls how users with multiple start events are anchored:
`"first_seen"` (anchor on first occurrence) or `"last_seen"` (anchor on most
recent).

### Right — 7-day retention

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "retention",
  "name": "7-day retention",
  "start_event": {
    "kind": "EventsNode",
    "event": "$pageview"
  },
  "completion_event": {
    "kind": "EventsNode",
    "event": "uploaded_file"
  },
  "retention_window_start": 0,
  "retention_window_end": 7,
  "retention_window_unit": "day",
  "start_handling": "first_seen"
}
```

### Wrong — missing `retention_window_start` and `start_handling`

```json
{
  "kind": "ExperimentMetric",
  "metric_type": "retention",
  "name": "7-day retention",
  "start_event": { "kind": "EventsNode", "event": "$pageview" },
  "completion_event": { "kind": "EventsNode", "event": "uploaded_file" },
  "retention_window_end": 7,
  "retention_window_unit": "day"
}
```

Pydantic rejects the payload with a missing-field error. Both fields are
required on every retention metric — the schema is the source of truth.

## Adding metrics to an experiment

Call `experiment-update` with the full `metrics` array. This **replaces** the
entire list.

To add a metric without losing existing ones:

1. Call `experiment-get` to get current metrics
2. Append the new metric to the existing array
3. Call `experiment-update` with the combined array

## Property filters

Any `EventsNode` can include property filters to narrow *which* events count.
Filters never change aggregation — for that, use `math` / `math_property`.

```json
{
  "kind": "EventsNode",
  "event": "purchase_completed",
  "properties": [
    {
      "key": "plan",
      "value": ["pro", "enterprise"],
      "operator": "exact",
      "type": "event"
    }
  ]
}
```
