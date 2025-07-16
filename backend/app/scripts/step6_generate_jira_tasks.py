#!/usr/bin/env python3
"""
Jira Task Creator Script

This script creates Jira tasks and sub-tasks based on the tasks defined in
.taskmaster/tasks/tasks.json, respecting dependencies and project structure.

Required Environment Variables:
- JIRA_BASE_URL: Jira instance URL (e.g., https://yourcompany.atlassian.net)
- JIRA_EMAIL: Jira account email
- JIRA_API_TOKEN: Jira API token (not password)
- JIRA_PROJECT_KEY: Jira project key (e.g., PROJ)
- JIRA_ASSIGNEE_ACCOUNT_ID: Default assignee account ID (optional)

Usage:
    python create_jira_tasks.py [--dry-run] [--project-key PROJ] [--epic-key EPIC-123]

Options:
    --dry-run: Preview what would be created without making actual changes
    --project-key: Override JIRA_PROJECT_KEY
    --epic-key: Create all tasks under a specific epic
    --start-from: Start creating tasks from a specific task ID
"""

import json
import os
import sys
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv # Corrected import for load_dotenv

load_dotenv()


try:
    from jira import JIRA
    from jira.exceptions import JIRAError
except ImportError:
    print("Error: jira package not found. Install with: pip install jira")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JiraTaskCreator:
    def __init__(self, base_url: str, email: str, api_token: str, project_key: str):
        """Initialize Jira connection."""
        self.jira = JIRA(
            server=base_url,
            basic_auth=(email, api_token)
        )
        self.project_key = project_key
        # Map task_id -> Jira issue_key for both main tasks and subtasks
        self.created_issues = {}
        
    def load_tasks(self, file_path: str = ".taskmaster/tasks/tasks.json") -> Dict[str, Any]:
        """Load tasks from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            logger.error(f"Tasks file not found: {file_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in tasks file: {e}")
            sys.exit(1)
    
    def create_issue(self, task: Dict[str, Any], parent_key: Optional[str] = None, is_subtask: bool = False) -> Optional[str]:
        """
        Create a Jira issue from a task.
        Args:
            task (Dict): The task dictionary.
            parent_key (Optional[str]): The Jira issue key of the parent task, if this is a sub-task.
            is_subtask (bool): True if this task should be created as a sub-task.
        Returns:
            Optional[str]: The created Jira issue key, or None if creation failed.
        """
        # Map task priority to Jira priority
        priority_map = {
            "high": "High",
            "medium": "Medium", 
            "low": "Low"
        }
        
        issue_type_name = "Subtask" if is_subtask else "Task"

        # Create issue fields
        fields = {
            "project": {"key": self.project_key},
            "summary": task["title"],
            "description": self.format_description(task),
            "issuetype": {"name": issue_type_name},
            "priority": {"name": priority_map.get(task.get("priority", "medium"), "Medium")}
        }
        
        if parent_key:
            # For sub-tasks, the 'parent' field is required
            fields["parent"] = {"key": parent_key}
        
        # Add assignee if provided
        assignee_account_id = os.getenv("JIRA_ASSIGNEE_ACCOUNT_ID")
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        
        try:
            issue = self.jira.create_issue(fields=fields)
            logger.info(f"Created {issue_type_name}: {issue.key} - {task['title']}")
            return issue.key
        except JIRAError as e:
            logger.error(f"Failed to create {issue_type_name} for task {task.get('id', task.get('title'))}: {e}")
            # Log the full error details if available
            if e.text:
                logger.error(f"Jira API Error Details: {e.text}")
            return None
    
    def format_description(self, task: Dict[str, Any]) -> str:
        """Format task description for Jira."""
        description_parts = []
        
        # Add main description
        if task.get("description"):
            description_parts.append(f"h2. Description\n{task['description']}")
        
        # Add details
        if task.get("details"):
            details = task["details"]
            # Ensure details is treated as a string, join if it's a list
            if isinstance(details, list):
                details = "\n".join(details)
            description_parts.append(f"h2. Implementation Details\n{details}")
        
        # Add test strategy
        if task.get("testStrategy"):
            test_strategy = task["testStrategy"]
            # Ensure testStrategy is treated as a string, join if it's a list
            if isinstance(test_strategy, list):
                test_strategy = "\n".join(test_strategy)
            description_parts.append(f"h2. Test Strategy\n{test_strategy}")
        
        # Add dependencies (only for main tasks, subtasks implicitly depend on parent)
        # This part assumes dependencies refer to other top-level tasks.
        # If subtasks have explicit dependencies on other tasks/subtasks,
        # more complex logic would be needed.
        if "id" in task and task.get("dependencies"): # Only show dependencies for top-level tasks with IDs
            deps = ", ".join(map(str, task["dependencies"]))
            description_parts.append(f"h2. Dependencies\nTasks: {deps}")
        
        # Add metadata
        metadata_parts = [
            f"* Task ID: {task.get('id', 'N/A')}", # Use .get for robustness
            f"* Priority: {task.get('priority', 'medium')}",
            f"* Status: {task.get('status', 'pending')}"
        ]
        if task.get("assignedTo"): # Add assignedTo if present in the task structure
            metadata_parts.append(f"* Assigned To: {task['assignedTo']}")

        description_parts.append(
            f"h2. Metadata\n" + "\n".join(metadata_parts)
        )
        
        return "\n\n".join(description_parts)
    
    def resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort tasks based on dependencies using topological sort."""
        # Create a map of task_id -> task
        task_map = {task["id"]: task for task in tasks}
        
        # Build dependency graph
        graph = {task["id"]: set(task.get("dependencies", [])) for task in tasks}
        
        # Topological sort
        visited = set()
        recursion_stack = set() # To detect cycles
        result = []
        
        def dfs(task_id):
            visited.add(task_id)
            recursion_stack.add(task_id)
            
            for dep_id in graph[task_id]:
                if dep_id not in task_map:
                    logger.warning(f"Dependency {dep_id} for task {task_id} not found in task list. Skipping.")
                    continue
                if dep_id not in visited:
                    dfs(dep_id)
                elif dep_id in recursion_stack:
                    logger.error(f"Cycle detected in dependencies involving task {task_id} and {dep_id}. This may lead to infinite loop or incorrect order.")
            
            recursion_stack.remove(task_id)
            result.append(task_map[task_id])
        
        for task in tasks:
            if task["id"] not in visited:
                dfs(task["id"])
        
        # Reverse the result to get correct topological order
        return result[::-1]
    
    def create_tasks(self, tasks_data: Dict[str, Any], epic_key: Optional[str] = None, 
                    start_from: Optional[int] = None, dry_run: bool = False) -> None:
        """Create all tasks and their sub-tasks from the tasks.json file."""
        if "master" not in tasks_data or "tasks" not in tasks_data["master"]:
            logger.error("Invalid tasks.json structure: 'master' or 'tasks' key not found.")
            return

        main_tasks = tasks_data["master"]["tasks"]
        
        # Filter tasks if start_from is specified
        if start_from:
            main_tasks = [t for t in main_tasks if t["id"] >= start_from]
        
        # Resolve dependencies to create main tasks in correct order
        sorted_main_tasks = self.resolve_dependencies(main_tasks)
        
        logger.info(f"Creating {len(sorted_main_tasks)} main tasks...")
        
        for main_task in sorted_main_tasks:
            logger.info(f"Processing main task: {main_task['title']} (ID: {main_task['id']})")
            
            main_issue_key = None
            if dry_run:
                main_issue_key = f"DRY-TASK-{main_task['id']}"
                logger.info(f"[DRY RUN] Would create main task: {main_issue_key} - {main_task['title']}")
            else:
                main_issue_key = self.create_issue(main_task, parent_key=epic_key, is_subtask=False)
            
            if main_issue_key:
                self.created_issues[main_task["id"]] = main_issue_key
                
                # Check for and create sub-tasks
                subtasks = main_task.get("subtasks", [])
                if subtasks:
                    logger.info(f"  Creating {len(subtasks)} sub-tasks for {main_issue_key}...")
                    for subtask in subtasks:
                        # Sub-tasks do not have their own dependencies in this model,
                        # they implicitly depend on their parent.
                        if dry_run:
                            sub_issue_key = f"DRY-SUBTASK-{main_task['id']}-{subtask['id']}"
                            logger.info(f"  [DRY RUN] Would create sub-task: {sub_issue_key} - {subtask['title']} under {main_issue_key}")
                        else:
                            sub_issue_key = self.create_issue(subtask, parent_key=main_issue_key, is_subtask=True)
                        
                        if sub_issue_key:
                            # Store subtask ID with a composite key or similar if IDs are not unique across tasks
                            # For simplicity, assuming subtask IDs are unique within a parent task.
                            # If not, you might need a key like f"{main_task['id']}-{subtask['id']}"
                            self.created_issues[f"{main_task['id']}-{subtask['id']}"] = sub_issue_key
            else:
                logger.error(f"Skipping sub-task creation for main task {main_task['id']} as parent issue was not created.")
        
        logger.info("Task and sub-task creation completed!")
        logger.info(f"Created issues: {self.created_issues}")
    
    def create_epic(self, title: str = "TodoList Application Development", 
                   description: str = "Epic for TodoList application development project") -> Optional[str]:
        """Create an epic to group all tasks."""
        fields = {
            "project": {"key": self.project_key},
            "summary": title,
            "description": description,
            "issuetype": {"name": "Epic"}
        }
        
        try:
            epic = self.jira.create_issue(fields=fields)
            logger.info(f"Created epic: {epic.key}")
            return epic.key
        except JIRAError as e:
            logger.error(f"Failed to create epic: {e}")
            if e.text:
                logger.error(f"Jira API Error Details: {e.text}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Create Jira tasks from tasks.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--project-key", help="Override JIRA_PROJECT_KEY")
    parser.add_argument("--epic-key", help="Create tasks under existing epic")
    parser.add_argument("--create-epic", action="store_true", help="Create new epic")
    parser.add_argument("--start-from", type=int, help="Start from specific task ID")
    
    args = parser.parse_args()
    
    # Get configuration from environment or arguments
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")
    project_key = args.project_key or os.getenv("JIRA_PROJECT_KEY")
    
    if not all([base_url, email, api_token, project_key]):
        print("Error: Missing required environment variables", file=sys.stderr)
        print("Required: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY", file=sys.stderr)
        sys.exit(1)
    
    # Create Jira client
    creator = JiraTaskCreator(base_url, email, api_token, project_key)
    
    # Load tasks
    tasks_data = creator.load_tasks()
    
    # Create epic if requested
    epic_key = None
    if args.create_epic and not args.dry_run:
        epic_key = creator.create_epic()
    elif args.epic_key:
        epic_key = args.epic_key
    
    # Create tasks
    creator.create_tasks(
        tasks_data,
        epic_key=epic_key,
        start_from=args.start_from,
        dry_run=args.dry_run
    )
    
    if args.dry_run:
        print("\nDRY RUN completed. No actual changes made.")
        print("To create tasks, run without --dry-run flag")

if __name__ == "__main__":
    main()
