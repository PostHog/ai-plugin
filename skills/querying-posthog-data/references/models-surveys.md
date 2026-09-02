# Surveys

## Survey (`system.surveys`)

Surveys collect feedback from users through questions and forms.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Survey id (UUID).
`team_id` | Integer | NOT NULL |
`name` | String | NOT NULL | Survey name.
`type` | String | NOT NULL | Survey delivery type, e.g. 'popover', 'api', 'widget'.
`questions` | JSON | NOT NULL | JSON array of the survey's questions.
`appearance` | JSON | NOT NULL | JSON styling/appearance configuration.
`start_date` | DateTime | NOT NULL | When the survey was launched; NULL if not started.
`end_date` | DateTime | NOT NULL | When the survey was stopped; NULL if still running.
`created_by_id` | Integer | NULL | User who created the survey.
`created_at` | DateTime | NOT NULL | When the survey was created.

### Question Types

```json
[
  {
    "id": "uuid",
    "type": "open",
    "question": "How can we improve?",
    "optional": false,
    "buttonText": "Submit"
  },
  {
    "id": "uuid",
    "type": "rating",
    "question": "How would you rate us?",
    "display": "number",
    "scale": 10,
    "lowerBoundLabel": "Not likely",
    "upperBoundLabel": "Very likely"
  },
  {
    "id": "uuid",
    "type": "single_choice",
    "question": "Which feature do you use most?",
    "choices": ["Feature A", "Feature B", "Feature C"]
  }
]
```

### Key Relationships

- **Feature Flags**: Multiple flag relationships via `system.feature_flags`

### Important Notes

- Survey name must be unique per team
- Internal flags (`targeting_flag`, `internal_targeting_flag`, `internal_response_sampling_flag`) are auto-managed
- `linked_flag` is user-managed and optional

## SurveyResponseArchive (`system.survey_response_archives`)

Survey responses are stored as events, so archiving one is recorded in Postgres instead. One row per archived (hidden) response.

### Columns

Column | Type | Nullable | Description
`id` | UUID | NOT NULL | Archive record UUID.
`team_id` | Integer | NOT NULL |
`survey_id` | UUID | NOT NULL | Survey the archived response belongs to; joins to surveys.id.
`response_uuid` | UUID | NOT NULL | UUID of the event holding the response; joins to events.uuid.
`archived_at` | DateTime | NOT NULL | When the response was archived.

### Key Relationships

- **Archived responses**: `system.survey_response_archives.survey_id` -> `system.surveys.id`

### Important Notes

- To exclude archived responses from a survey's results, anti-join the survey events against this table on `events.uuid = survey_response_archives.response_uuid`
- `(team_id, response_uuid)` is unique
