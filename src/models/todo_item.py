"""
Todo item model following todo.txt syntax.
"""
import re
from datetime import datetime
from typing import List, Optional


class TodoItem:
    """Represents a single todo item following todo.txt syntax."""
    
    def __init__(self, raw_text: str = ""):
        self.raw_text = raw_text.strip()
        self.completed = False
        self.priority = None
        self.completion_date = None
        self.creation_date = None
        self.description = ""
        self.projects = []
        self.contexts = []
        self.due_date = None
        
        self._parse()
    
    def _parse(self):
        """Parse the raw text according to todo.txt syntax."""
        if not self.raw_text:
            return
            
        text = self.raw_text
        
        # Check if completed
        if text.startswith('x '):
            self.completed = True
            text = text[2:]  # Remove 'x '
            
            # Extract completion date if present
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+', text)
            if date_match:
                try:
                    self.completion_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                    text = text[len(date_match.group(0)):]
                except ValueError:
                    pass
        
        # Extract priority
        priority_match = re.match(r'^\(([A-Z])\)\s+', text)
        if priority_match:
            self.priority = priority_match.group(1)
            text = text[len(priority_match.group(0)):]
        
        # Extract creation date if present and not already parsed as completion date
        if not self.completion_date:
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+', text)
            if date_match:
                try:
                    self.creation_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                    text = text[len(date_match.group(0)):]
                except ValueError:
                    pass
        
        # Extract projects (+project)
        self.projects = re.findall(r'\+(\w+)', text)
        
        # Extract contexts (@context)
        self.contexts = re.findall(r'@(\w+)', text)
        
        # Extract due date (due:YYYY-MM-DD)
        due_match = re.search(r'due:(\d{4}-\d{2}-\d{2})', text)
        if due_match:
            try:
                self.due_date = datetime.strptime(due_match.group(1), '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # The remaining text is the description
        self.description = text.strip()
    
    def to_string(self) -> str:
        """Convert the todo item back to todo.txt format."""
        parts = []
        
        # Completion marker
        if self.completed:
            parts.append('x')
            if self.completion_date:
                parts.append(self.completion_date.strftime('%Y-%m-%d'))
        
        # Priority
        if self.priority and not self.completed:
            parts.append(f'({self.priority})')
        
        # Creation date
        if self.creation_date and not self.completed:
            parts.append(self.creation_date.strftime('%Y-%m-%d'))
        
        # Description with projects and contexts
        parts.append(self.description)
        
        return ' '.join(parts)
    
    def toggle_completion(self):
        """Toggle the completion status of the todo item."""
        self.completed = not self.completed
        if self.completed:
            self.completion_date = datetime.now().date()
        else:
            self.completion_date = None
    
    def set_priority(self, priority: Optional[str]):
        """Set the priority of the todo item."""
        if priority and priority.upper() in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            self.priority = priority.upper()
        else:
            self.priority = None
    
    def add_project(self, project: str):
        """Add a project to the todo item."""
        if project not in self.projects:
            self.projects.append(project)
            self.description = f"{self.description} +{project}".strip()
    
    def add_context(self, context: str):
        """Add a context to the todo item."""
        if context not in self.contexts:
            self.contexts.append(context)
            self.description = f"{self.description} @{context}".strip()
    
    def set_due_date(self, due_date: Optional[datetime]):
        """Set the due date of the todo item."""
        if due_date:
            self.due_date = due_date.date() if isinstance(due_date, datetime) else due_date
            # Add or update due date in description
            due_pattern = r'due:\d{4}-\d{2}-\d{2}'
            if re.search(due_pattern, self.description):
                self.description = re.sub(due_pattern, f'due:{self.due_date}', self.description)
            else:
                self.description = f"{self.description} due:{self.due_date}".strip()
        else:
            self.due_date = None
            # Remove due date from description
            self.description = re.sub(r'\s*due:\d{4}-\d{2}-\d{2}', '', self.description).strip()
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return f"TodoItem('{self.to_string()}')"
