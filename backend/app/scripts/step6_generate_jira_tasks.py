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
from load_dotenv import load_dotenv

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
        self.created_issues = {}  # Map task_id -> issue_key
        
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
    
    def create_issue(self, task: Dict[str, Any], parent_key: Optional[str] = None) -> str:
        """Create a Jira issue from a task."""
        # Map task priority to Jira priority
        priority_map = {
            "high": "High",
            "medium": "Medium", 
            "low": "Low"
        }
        
        # Create issue fields
        fields = {
            "project": {"key": self.project_key},
            "summary": task["title"],
            "description": self.format_description(task),
            "issuetype": {"name": "Task"},
            "priority": {"name": priority_map.get(task.get("priority", "medium"), "Medium")}
        }
        
        if parent_key:
            fields["parent"] = {"key": parent_key}
        
        # Add assignee if provided
        assignee_account_id = os.getenv("JIRA_ASSIGNEE_ACCOUNT_ID")
        if assignee_account_id:
            fields["assignee"] = {"accountId": assignee_account_id}
        
        try:
            issue = self.jira.create_issue(fields=fields)
            logger.info(f"Created issue: {issue.key} - {task['title']}")
            return issue.key
        except JIRAError as e:
            logger.error(f"Failed to create issue for task {task['id']}: {e}")
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
            if isinstance(details, list):
                details = "\n".join(details)
            description_parts.append(f"h2. Implementation Details\n{details}")
        
        # Add test strategy
        if task.get("testStrategy"):
            test_strategy = task["testStrategy"]
            if isinstance(test_strategy, list):
                test_strategy = "\n".join(test_strategy)
            description_parts.append(f"h2. Test Strategy\n{test_strategy}")
        
        # Add dependencies
        if task.get("dependencies"):
            deps = ", ".join(map(str, task["dependencies"]))
            description_parts.append(f"h2. Dependencies\nTasks: {deps}")
        
        # Add metadata
        description_parts.append(
            f"h2. Metadata\n"
            f"* Task ID: {task['id']}\n"
            f"* Priority: {task.get('priority', 'medium')}\n"
            f"* Status: {task.get('status', 'pending')}"
        )
        
        return "\n\n".join(description_parts)
    
    def resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort tasks based on dependencies."""
        # Create a map of task_id -> task
        task_map = {task["id"]: task for task in tasks}
        
        # Build dependency graph
        graph = {task["id"]: set(task.get("dependencies", [])) for task in tasks}
        
        # Topological sort
        visited = set()
        result = []
        
        def dfs(task_id):
            if task_id in visited:
                return
            visited.add(task_id)
            
            for dep_id in graph[task_id]:
                if dep_id in task_map:
                    dfs(dep_id)
            
            result.append(task_map[task_id])
        
        for task in tasks:
            if task["id"] not in visited:
                dfs(task["id"])
        
        return result
    
    def create_tasks(self, tasks_data: Dict[str, Any], epic_key: Optional[str] = None, 
                    start_from: Optional[int] = None, dry_run: bool = False) -> None:
        """Create all tasks from the tasks.json file."""
        tasks = tasks_data["master"]["tasks"]
        
        # Filter tasks if start_from is specified
        if start_from:
            tasks = [t for t in tasks if t["id"] >= start_from]
        
        # Resolve dependencies to create tasks in correct order
        sorted_tasks = self.resolve_dependencies(tasks)
        
        logger.info(f"Creating {len(sorted_tasks)} tasks...")
        
        for task in sorted_tasks:
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {task['title']} (ID: {task['id']})")
                self.created_issues[task["id"]] = f"DRY-{task['id']}"
            else:
                issue_key = self.create_issue(task, parent_key=epic_key)
                if issue_key:
                    self.created_issues[task["id"]] = issue_key
        
        logger.info("Task creation completed!")
        logger.info(f"Created issues: {self.created_issues}")
    
    def create_epic(self, title: str = "TodoList Application Development", 
                   description: str = "Epic for TodoList application development project") -> str:
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
        print("Error: Missing required environment variables")
        print("Required: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY")
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