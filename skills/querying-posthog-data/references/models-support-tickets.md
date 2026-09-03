# Support Tickets

## Ticket (`system.support_tickets`)

Support tickets from the conversations product, created via widget, email, or Slack channels.

### Columns

Column | Type | Nullable | Description
`id` | String | NOT NULL | Ticket UUID.
`team_id` | Integer | NOT NULL |
`ticket_number` | Integer | NOT NULL | Human-friendly sequential ticket number.
`organization_id` | String | NULL | Customer organization key. This matches a customer analytics account's external_id.
`channel_source` | String | NOT NULL | Channel the ticket came in on, e.g. 'email', 'widget'.
`channel_detail` | String | NULL | Additional channel detail, e.g. inbox or address.
`distinct_id` | String | NOT NULL | Distinct id of the person who opened the ticket.
`status` | String | NOT NULL | Ticket status: 'new', 'open', 'pending', 'on_hold', or 'resolved'.
`priority` | String | NULL | Ticket priority, e.g. 'low', 'high'.
`anonymous_traits` | JSON | NOT NULL | JSON traits captured for an anonymous requester.
`ai_resolved` | Integer | NOT NULL | 1 if the ticket was resolved by AI without human escalation, 0 otherwise.
`escalation_reason` | String | NULL | Why the ticket was escalated to a human, if it was.
`message_count` | Integer | NOT NULL | Total number of messages in the ticket.
`unread_customer_count` | Integer | NOT NULL | Messages unread by the customer.
`unread_team_count` | Integer | NOT NULL | Messages unread by the support team.
`last_message_at` | DateTime | NULL | When the most recent message was sent.
`last_message_text` | String | NULL | Text of the most recent message.
`email_subject` | String | NULL | Subject line for email-channel tickets.
`email_from` | String | NULL | Sender address for email-channel tickets.
`session_id` | String | NULL | Session recording id associated with the ticket, if any.
`session_context` | JSON | NOT NULL | JSON context captured from the user's session.
`sla_due_at` | DateTime | NULL | When the ticket's SLA response is due.
`created_at` | DateTime | NOT NULL | When the ticket was opened.
`updated_at` | DateTime | NOT NULL | When the ticket was last updated.

### Key Relationships

- Tickets belong to a **Team** (`team_id`)
- Tickets can link to a customer analytics account through `organization_id = system.accounts.external_id`
- Tickets are linked to a **Person** via `distinct_id`
- Ticket assignments are managed via `TicketAssignment` and queryable through `system.support_tickets.assignee`

### Important Notes

- The `status` field follows a lifecycle: `new` -> `open` -> `pending`/`on_hold` -> `resolved`
- The `anonymous_traits` field contains customer-provided key-value pairs, commonly including `name` and `email`
- The `session_context` field may contain `session_replay_url`, `current_url`, and other session metadata
- Tickets are never deleted; filter by `status` to exclude resolved tickets
