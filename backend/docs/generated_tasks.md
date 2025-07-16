🏷️ tag: master
Parsing PRD file: /Users/apoorvnag/apoorv-nag/todo-list/backend/.taskmaster_temp_input.txt
Generating 10 tasks...
[INFO] Parsing PRD file: /Users/apoorvnag/apoorv-nag/todo-list/backend/.taskmaster_temp_input.txt, Force: false, Append: false, Research: false
[INFO] Tag 'master' is empty or doesn't exist. Creating/updating tag with new tasks.
[INFO] Reading PRD content from /Users/apoorvnag/apoorv-nag/todo-list/backend/.taskmaster_temp_input.txt
[INFO] ✓ JSON schema validation enabled
[INFO] Calling AI service to generate tasks from PRD...
[INFO] New AI service call with role: main
[SUCCESS] Successfully parsed PRD via AI service.
[SUCCESS] Successfully generated 10 tasks in /Users/apoorvnag/apoorv-nag/todo-list/backend/.taskmaster/tasks/tasks.json
╭──────────────────────────────────────────────────────────────────────────────╮
│                                                                              │
│   Successfully generated 10 new tasks. Total tasks in /Users/apoorvnag/apo   │
│   orv-nag/todo-list/backend/.taskmaster/tasks/tasks.json: 10                 │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│   Next Steps:                                                              │
│                                                                            │
│   1. Run task-master list to view all tasks                                │
│   2. Run task-master expand --id=<id> to break down a task into subtasks   │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

╭────────────────── 💡 Telemetry ──────────────────╮
│                                                  │
│   AI Usage Summary:                              │
│     Command: parse-prd                           │
│     Provider: anthropic                          │
│     Model: claude-3-7-sonnet-20250219            │
│     Tokens: 16224 (Input: 12878, Output: 3346)   │
│     Est. Cost: $0.088824                         │
│                                                  │
╰──────────────────────────────────────────────────╯

╭──────────────────────────────────────────────────────────────────────────────╮
│  FYI: Taskmaster now supports separate task lists per tag. Use the --tag     │
│  flag to create/read/update/filter tasks by tag.                             │
╰──────────────────────────────────────────────────────────────────────────────╯

