"""
Todo list manager for reading and writing todo.txt files.
"""
import os
from typing import List, Optional
from datetime import datetime, date
from .todo_item import TodoItem


class TodoManager:
    """Manages todo items and file operations."""
    
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        self.todo_file = os.path.join(data_folder, 'todo.txt')
        self.items: List[TodoItem] = []
        self._ensure_data_folder()
        self.load_todos()
    
    def _ensure_data_folder(self):
        """Ensure the data folder exists."""
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def load_todos(self):
        """Load todos from the todo.txt file."""
        self.items = []
        if os.path.exists(self.todo_file):
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:  # Skip empty lines
                            self.items.append(TodoItem(line))
            except Exception as e:
                print(f"Error loading todos: {e}")
    
    def save_todos(self):
        """Save todos to the todo.txt file."""
        try:
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                for item in self.items:
                    f.write(item.to_string() + '\n')
        except Exception as e:
            print(f"Error saving todos: {e}")
    
    def add_todo(self, description: str, priority: Optional[str] = None) -> TodoItem:
        """Add a new todo item."""
        # Create item with raw text to trigger parsing of todo.txt format
        item = TodoItem(description)
        
        # Set creation date if not already parsed
        if not item.creation_date:
            item.creation_date = datetime.now().date()
        
        # Set priority only if not already parsed and explicitly provided
        if priority and not item.priority:
            item.set_priority(priority)
        
        self.items.append(item)
        self.save_todos()
        return item
    
    def remove_todo(self, item: TodoItem):
        """Remove a todo item."""
        if item in self.items:
            self.items.remove(item)
            self.save_todos()
    
    def update_todo(self, item: TodoItem):
        """Update a todo item and save."""
        self.save_todos()
    
    def get_todos_by_project(self, project: str) -> List[TodoItem]:
        """Get all todos for a specific project."""
        return [item for item in self.items if project in item.projects]
    
    def get_todos_by_context(self, context: str) -> List[TodoItem]:
        """Get all todos for a specific context."""
        return [item for item in self.items if context in item.contexts]
    
    def get_completed_todos(self) -> List[TodoItem]:
        """Get all completed todos."""
        return [item for item in self.items if item.completed]
    
    def get_pending_todos(self) -> List[TodoItem]:
        """Get all pending (not completed) todos."""
        return [item for item in self.items if not item.completed]
    
    def get_todos_due_today(self) -> List[TodoItem]:
        """Get todos due today."""
        today = date.today()
        return [item for item in self.get_pending_todos() 
                if item.due_date and item.due_date <= today]
    
    def get_todos_due_upcoming(self, days: int = 5) -> List[TodoItem]:
        """Get todos due in the next few days."""
        today = date.today()
        upcoming_date = date.fromordinal(today.toordinal() + days)
        return [item for item in self.get_pending_todos() 
                if item.due_date and today < item.due_date <= upcoming_date]
    
    def get_todos_someday(self) -> List[TodoItem]:
        """Get todos without a due date."""
        return [item for item in self.get_pending_todos() if not item.due_date]
    
    def get_all_projects(self) -> List[str]:
        """Get all unique projects."""
        projects = set()
        for item in self.items:
            projects.update(item.projects)
        return sorted(list(projects))
    
    def get_all_contexts(self) -> List[str]:
        """Get all unique contexts."""
        contexts = set()
        for item in self.items:
            contexts.update(item.contexts)
        return sorted(list(contexts))
    
    def sort_by_priority(self, items: List[TodoItem]) -> List[TodoItem]:
        """Sort todos by priority (A-Z, then no priority)."""
        def priority_key(item):
            if item.priority:
                return (0, item.priority)
            else:
                return (1, 'Z')  # No priority comes after Z
        
        return sorted(items, key=priority_key)
    
    def sort_by_due_date(self, items: List[TodoItem]) -> List[TodoItem]:
        """Sort todos by due date (earliest first, then no due date)."""
        def due_date_key(item):
            if item.due_date:
                return (0, item.due_date)
            else:
                return (1, date.max)  # No due date comes last
        
        return sorted(items, key=due_date_key)
