"""
Notes manager for handling Markdown notes.
"""
import os
import re
from typing import List, Optional
from datetime import datetime


class Note:
    """Represents a single Markdown note."""
    
    def __init__(self, filepath: str = "", content: str = ""):
        self.filepath = filepath
        self.content = content
        self.title = self._extract_title()
        self.modified_time = None
        if filepath and os.path.exists(filepath):
            self.modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
    
    def _extract_title(self) -> str:
        """Extract title from the first line of the note."""
        if not self.content:
            return "Untitled"
        
        lines = self.content.split('\n')
        if lines:
            # Remove markdown heading markers
            title = lines[0].strip()
            title = re.sub(r'^#+\s*', '', title)  # Remove # markers
            return title if title else "Untitled"
        return "Untitled"
    
    def update_content(self, content: str):
        """Update the note content and refresh title."""
        self.content = content
        self.title = self._extract_title()
    
    def save(self):
        """Save the note to file."""
        if not self.filepath:
            return False
        
        try:
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(self.content)
            self.modified_time = datetime.now()
            return True
        except Exception as e:
            print(f"Error saving note: {e}")
            return False
    
    def delete(self):
        """Delete the note file."""
        if self.filepath and os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
                return True
            except Exception as e:
                print(f"Error deleting note: {e}")
                return False
        return False


class NotesManager:
    """Manages notes and file operations."""
    
    def __init__(self, data_folder: str):
        self.data_folder = data_folder
        self.notes_folder = os.path.join(data_folder, 'notes')
        self.notes: List[Note] = []
        self._ensure_notes_folder()
        self.load_notes()
    
    def _ensure_notes_folder(self):
        """Ensure the notes folder exists."""
        if not os.path.exists(self.notes_folder):
            os.makedirs(self.notes_folder)
    
    def load_notes(self):
        """Load all notes from the notes folder."""
        self.notes = []
        if not os.path.exists(self.notes_folder):
            return
        
        try:
            for filename in os.listdir(self.notes_folder):
                if filename.endswith('.md'):
                    filepath = os.path.join(self.notes_folder, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        note = Note(filepath, content)
                        self.notes.append(note)
                    except Exception as e:
                        print(f"Error loading note {filename}: {e}")
        except Exception as e:
            print(f"Error loading notes: {e}")
    
    def create_note(self, title: str = "New Note", content: str = "") -> Note:
        """Create a new note."""
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        safe_title = safe_title.strip('-')
        
        if not safe_title:
            safe_title = "untitled"
        
        # Ensure unique filename
        base_filename = safe_title
        counter = 1
        while True:
            filename = f"{safe_title}.md"
            filepath = os.path.join(self.notes_folder, filename)
            if not os.path.exists(filepath):
                break
            safe_title = f"{base_filename}-{counter}"
            counter += 1
        
        # Create initial content if not provided
        if not content:
            content = f"# {title}\n\n"
        
        note = Note(filepath, content)
        note.save()
        self.notes.append(note)
        return note
    
    def delete_note(self, note: Note):
        """Delete a note."""
        if note in self.notes:
            note.delete()
            self.notes.remove(note)
    
    def save_note(self, note: Note):
        """Save a note."""
        note.save()
    
    def search_notes(self, query: str) -> List[Note]:
        """Search notes by content."""
        if not query:
            return self.notes
        
        query_lower = query.lower()
        matching_notes = []
        
        for note in self.notes:
            # Search in title and content
            if (query_lower in note.title.lower() or 
                query_lower in note.content.lower()):
                matching_notes.append(note)
        
        return matching_notes
    
    def get_notes_by_title_sorted(self) -> List[Note]:
        """Get notes sorted by title."""
        return sorted(self.notes, key=lambda note: note.title.lower())
    
    def get_notes_by_modified_date(self) -> List[Note]:
        """Get notes sorted by modification date (newest first)."""
        return sorted(self.notes, key=lambda note: note.modified_time or datetime.min, reverse=True)
    
    def refresh_notes(self):
        """Refresh the notes list from the filesystem."""
        self.load_notes()
