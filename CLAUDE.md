# Inbox Workflow

When the user asks "what's in my inbox" or similar:

1. Read `inbox.json` in this directory
2. List all tasks with status "pending"
3. Ask which task(s) to work on (or work through all if asked)
4. For each task, do the heavy work (write code, research, download, etc.)
5. After completing a task, update its status to "done" and fill in the "result" field in inbox.json
