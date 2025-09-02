"""
DoNotePad - A lightweight productivity app using Flet (Flutter for Python).
"""
import flet as ft
import os
import json
from datetime import datetime, date, timedelta
from src.models.todo_manager import TodoManager
from src.models.notes_manager import NotesManager, Note
from src.models.todo_item import TodoItem


class DoNotePadApp:
    """Main DoNotePad application using Flet."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.todo_manager = None
        self.notes_manager = None
        self.data_folder = None
        self.current_note = None
        self.note_has_unsaved_changes = False
        self.config_file = os.path.expanduser("~/.donotepad_config.json")
        
        # Auto-save configuration (simplified)
        self.auto_save_delay = 10  # Default 10 seconds (kept for config compatibility)
        self.auto_save_enabled = True  # Kept for config compatibility
        
        # Filter state
        self.date_filter = "all"
        self.selected_context = "all"
        self.selected_project = "all"
        self.current_tab = 0
        
        # UI components
        self.data_folder_display = None
        self.todo_list_view = None
        self.notes_list_view = None
        self.note_editor = None
        self.note_status_text = None
        self.save_button = None
        self.todo_filter_buttons = {}
        self.context_filter_buttons = {}
        self.project_filter_buttons = {}
        self.context_filter_dropdown = None
        self.project_filter_dropdown = None
        self.sort_buttons = None
        self.main_tabs = None
        self.current_dialog = None
        
        # Load configuration
        self.load_config()
        
        self.setup_page()
        self.build_ui()
        
        # Auto-load data folder if available
        if self.data_folder and os.path.exists(self.data_folder):
            self.set_data_folder(self.data_folder)
        else:
            pass  # No valid data folder to auto-load
        
        # Show welcome message if no data folder is set
        self.page.on_route_change = lambda _: None
    
    def on_tab_change(self, e):
        """Handle tab changes."""
        # Check for unsaved changes before switching
        if self.current_note and self.note_has_unsaved_changes:
            # Prevent the tab change and show save dialog
            self.show_save_before_navigation_dialog(
                lambda: self.switch_to_tab(e.control.selected_index)
            )
            return
        
        if e.control.selected_index == 0:  # Todos tab
            self.content_area.content = self.build_todo_section()
            self.current_tab = 0
            # Refresh todos after UI is built
            if self.todo_manager:
                self.page.update()  # Ensure UI is updated first
                self.refresh_todos()
                self.update_context_filter()
                self.update_project_filter()
        else:  # Notes tab
            self.content_area.content = self.build_notes_section()
            self.current_tab = 1
            # Refresh notes after UI is built
            if self.notes_manager:
                self.page.update()  # Ensure UI is updated first
                self.refresh_notes()
        self.page.update()
    
    def switch_to_tab(self, tab_index):
        """Programmatically switch to a tab."""
        # Update the tab component's selected index
        if hasattr(self, 'tab_component') and self.tab_component:
            self.tab_component.selected_index = tab_index
        
        if tab_index == 0:  # Todos tab
            self.content_area.content = self.build_todo_section()
            self.current_tab = 0
            # Refresh todos after UI is built
            if self.todo_manager:
                self.page.update()  # Ensure UI is updated first
                self.refresh_todos()
                self.update_context_filter()
                self.update_project_filter()
        else:  # Notes tab
            self.content_area.content = self.build_notes_section()
            self.current_tab = 1
            # Refresh notes after UI is built
            if self.notes_manager:
                self.page.update()  # Ensure UI is updated first
                self.refresh_notes()
        self.page.update()
        
    def setup_page(self):
        """Configure the page settings."""
        self.page.title = "DoNotePad"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 900
        self.page.window_height = 700
        self.page.window_min_width = 400
        self.page.window_min_height = 500
        self.page.padding = 10
        
        # Add keyboard event handler
        self.page.on_keyboard_event = self.on_keyboard_event
        
        # Add window close event handler
        self.page.on_window_event = self.on_window_event
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.data_folder = config.get('data_folder')
                    self.auto_save_delay = config.get('auto_save_delay', 10)
                    self.auto_save_enabled = config.get('auto_save_enabled', True)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                'data_folder': self.data_folder,
                'auto_save_delay': self.auto_save_delay,
                'auto_save_enabled': self.auto_save_enabled
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def on_window_event(self, e):
        """Handle window events like closing."""
        if e.data == "close":
            if self.current_note and self.note_has_unsaved_changes:
                # Prevent the window from closing immediately
                e.prevent_default = True
                self.show_save_on_close_dialog()
            # If no unsaved changes, let the window close normally
    
    def on_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard events for shortcuts."""
        if e.key == "Escape":
            # ESC: Close any open dialog
            if self.current_dialog:
                self.page.close(self.current_dialog)
                self.current_dialog = None
                return
        
        if e.ctrl and e.key == "Enter":
            # CTRL+ENTER: Save and close dialog if it's a todo dialog
            if self.current_dialog:
                # Find the save/create button and click it only for todo dialogs
                dialog_actions = self.current_dialog.actions
                if dialog_actions:
                    # Look for todo-related buttons specifically
                    for action in reversed(dialog_actions):
                        if hasattr(action, 'text') and action.text in ["Add Todo", "Save Changes"]:
                            action.on_click(None)
                            return
                return
        
        if e.ctrl:
            if e.key == "N":
                # CTRL-N: Create new item based on current tab
                if self.current_tab == 0:  # Todos tab
                    self.add_todo_dialog(None)
                elif self.current_tab == 1:  # Notes tab
                    # Check for unsaved changes before creating new note
                    if self.current_note and self.note_has_unsaved_changes:
                        self.show_save_before_navigation_dialog(
                            lambda: self.new_note_dialog(None)
                        )
                    else:
                        self.new_note_dialog(None)
            elif e.key == "T":
                # CTRL-T: Switch between tabs
                # Check for unsaved changes before switching
                if self.current_note and self.note_has_unsaved_changes:
                    new_tab = 1 if self.current_tab == 0 else 0
                    self.show_save_before_navigation_dialog(
                        lambda: self.switch_to_tab(new_tab)
                    )
                else:
                    new_tab = 1 if self.current_tab == 0 else 0
                    self.switch_to_tab(new_tab)
            elif e.key == "S":
                # CTRL-S: Save current note
                if self.current_tab == 1 and self.current_note:
                    self.save_current_note(None)
        
    def build_ui(self):
        """Build the user interface."""
        # Create compact data folder section for header
        self.data_folder_display = ft.Text(
            self.data_folder if self.data_folder else "No folder selected",
            size=12,
            color=ft.Colors.GREY_600,
        )
        
        compact_folder_section = ft.Row(
            [
                ft.Icon(ft.Icons.FOLDER_OPEN, size=16, color=ft.Colors.GREY_600),
                self.data_folder_display,
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_size=16,
                    tooltip="Change data folder",
                    on_click=self.select_data_folder,
                ),
            ],
            spacing=5,
        )
        
        # Main content area with tabs and folder info
        self.tab_component = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="📝 Todos"),
                ft.Tab(text="📄 Notes"),
            ],
            on_change=self.on_tab_change,
            divider_color=ft.Colors.TRANSPARENT,  # Remove the built-in tab divider
        )
        
        tab_header = ft.Row(
            [
                ft.Container(
                    self.tab_component,
                    expand=True,
                ),
                compact_folder_section,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Content area
        self.content_area = ft.Container(
            content=self.build_todo_section(),  # Start with todos
            expand=True,
        )
        
        # Add everything to page
        self.page.add(
            ft.Column(
                [
                    tab_header,
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    self.content_area,
                ],
                expand=True,
            )
        )
    
    def build_todo_section(self):
        """Build the todo section with filters and list."""
        # Filter panel
        filter_panel = self.build_todo_filters()
        
        # Todo list
        self.todo_list_view = ft.ListView(
            expand=1,
            spacing=5,
            padding=ft.padding.all(10),
        )
        
        # Sort options
        self.sort_buttons = ft.SegmentedButton(
            segments=[
                ft.Segment(
                    value="default",
                    icon=ft.Icon(ft.Icons.LIST),
                ),
                ft.Segment(
                    value="priority", 
                    icon=ft.Icon(ft.Icons.PRIORITY_HIGH),
                ),
                ft.Segment(
                    value="due_date",
                    icon=ft.Icon(ft.Icons.CALENDAR_TODAY),
                ),
            ],
            selected={"default"},
            show_selected_icon=False,
            style=ft.ButtonStyle(
                side=ft.BorderSide(
                    color=ft.Colors.INDIGO_100,
                    width=1,
                )
            ),
            on_change=lambda _: self.refresh_todos(),
        )
        
        # Action buttons
        action_buttons = ft.Row(
            [
                ft.Row([
                    ft.ElevatedButton(
                        "Add Todo",
                        icon=ft.Icons.ADD,
                        on_click=self.add_todo_dialog,
                    ),
                    ft.ElevatedButton(
                        "Refresh",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda _: self.refresh_todos(),
                    ),
                ], spacing=10),
                self.sort_buttons,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # Main todo content
        todo_content = ft.Column(
            [
                action_buttons,
                ft.Divider(height=1),
                self.todo_list_view,
            ],
            expand=True,
        )
        
        todo_section = ft.Row(
            [
                ft.Container(
                    filter_panel,
                    width=220,
                    height=None,  # Allow dynamic height
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=5,
                    alignment=ft.alignment.top_left,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    todo_content,
                    expand=True,
                    padding=10,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        
        return todo_section
    
    def build_todo_filters(self):
        """Build the todo filter panel."""
        # Date filters
        date_filters = ft.Column(
            [
                self.create_filter_button("all", "All", "date", True),
                self.create_filter_button("today", "Today", "date", False),
                self.create_filter_button("upcoming", "Upcoming", "date", False),
                self.create_filter_button("someday", "Someday", "date", False),
                self.create_filter_button("completed", "Completed", "date", False),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.START,
        )
        
        # Context filter buttons (will be populated dynamically)
        self.context_filter_container = ft.Column(
            spacing=2, 
            alignment=ft.MainAxisAlignment.START
        )
        
        # Project filter buttons (will be populated dynamically)  
        self.project_filter_container = ft.Column(
            spacing=2, 
            alignment=ft.MainAxisAlignment.START
        )
        
        # Create scrollable content
        filter_content = ft.Column(
            [
                date_filters,
                ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                ft.Text("Projects", weight=ft.FontWeight.BOLD, size=14),
                self.project_filter_container,
                ft.Divider(height=2, color=ft.Colors.TRANSPARENT),
                ft.Text("Contexts", weight=ft.FontWeight.BOLD, size=14),
                self.context_filter_container,
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return filter_content
    
    def create_filter_button(self, filter_type: str, label: str, button_type: str = "date", selected: bool = False):
        """Create a unified filter button with todo count."""
        # Get count based on button type
        if button_type == "date":
            count = self.count_todos_by_date_filter(filter_type)
            onclick_func = lambda _: self.set_filter("date", filter_type)
            button_dict = self.todo_filter_buttons
            selected_color = ft.Colors.BLUE_100
        elif button_type == "context":
            count = self.count_todos_by_context(filter_type)
            onclick_func = lambda _: self.set_filter("context", filter_type)
            button_dict = self.context_filter_buttons
            selected_color = ft.Colors.GREEN_100
        else:  # project
            count = self.count_todos_by_project(filter_type)
            onclick_func = lambda _: self.set_filter("project", filter_type)
            button_dict = self.project_filter_buttons
            selected_color = ft.Colors.PURPLE_100
        
        # Create a row with label on left and count on right
        button_content = ft.Row(
            [
                ft.Text(label, size=13, weight=ft.FontWeight.W_500),
                ft.Container(
                    content=ft.Text(
                        str(count), 
                        size=11, 
                        weight=ft.FontWeight.W_400,
                        color=ft.Colors.GREY_700
                    ),
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=ft.border_radius.all(8),
                    padding=ft.padding.symmetric(vertical=2, horizontal=6),
                    height=20,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        button = ft.TextButton(
            content=button_content,
            on_click=onclick_func,
            style=ft.ButtonStyle(
                bgcolor=selected_color if selected else None,
                color=ft.Colors.BLUE_900 if button_type == "date" and selected else 
                      ft.Colors.GREEN_900 if button_type == "context" and selected else 
                      ft.Colors.PURPLE_900 if button_type == "project" and selected else 
                      ft.Colors.GREY_800,
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
            ),
            width=200 if button_type == "date" else None,
            expand=True if button_type != "date" else False,
        )
        button_dict[filter_type] = button
        return button

    def create_context_filter_button(self, context: str, label: str, selected: bool = False):
        """Create a context filter button with todo count."""
        return self.create_filter_button(context, label, "context", selected)

    def create_project_filter_button(self, project: str, label: str, selected: bool = False):
        """Create a project filter button with todo count."""
        return self.create_filter_button(project, label, "project", selected)
    
    def build_notes_section(self):
        """Build the notes section."""
        # Notes list
        self.notes_list_view = ft.ListView(
            expand=1,
            spacing=2,
            padding=ft.padding.symmetric(horizontal=0, vertical=5),
        )
        
        # Search box
        search_box = ft.TextField(
            label="Search notes...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.search_notes,
        )
        
        # Notes list panel
        notes_panel = ft.Column(
            [
                ft.Text("Notes", weight=ft.FontWeight.BOLD, size=18),
                search_box,
                ft.ElevatedButton(
                    "New Note",
                    icon=ft.Icons.ADD,
                    on_click=self.new_note_with_check,
                ),
                self.notes_list_view,
            ],
            spacing=5,
        )
        
        # Note editor
        self.note_editor = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Preview",
                    content=ft.Column([
                        ft.Container(
                            ft.Markdown(
                                value="Select a note to preview...",
                                expand=True,
                                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                auto_follow_links=True,
                            ),
                            expand=True,
                            padding=ft.padding.all(16),
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                        ),
                    ], expand=True, scroll=ft.ScrollMode.AUTO),
                ),
                ft.Tab(
                    text="Edit",
                    content=ft.TextField(
                        multiline=True,
                        expand=True,
                        text_size=14,
                        on_change=self.on_note_content_changed,
                    ),
                ),
            ],
            expand=True,
        )
        
        # Create status text and save button references
        self.note_status_text = ft.Text("", size=14, color=ft.Colors.GREY_600)
        self.save_button = ft.IconButton(
            ft.Icons.SAVE,
            tooltip="Save Note (Ctrl+S)",
            on_click=self.save_current_note,
        )
        
        # Editor panel with actions
        editor_panel = ft.Column(
            [
                ft.Row(
                    [
                        ft.Column([
                            ft.Text("Note Editor", weight=ft.FontWeight.BOLD, size=18),
                            self.note_status_text,
                        ], spacing=2),
                        ft.Row(
                            [
                                self.save_button,
                                ft.IconButton(
                                    ft.Icons.DELETE,
                                    tooltip="Delete Note",
                                    on_click=self.delete_current_note,
                                ),
                            ],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1),
                self.note_editor,
            ],
            expand=True,
        )
        
        notes_section = ft.Row(
            [
                ft.Container(
                    notes_panel,
                    width=220,
                    padding=5,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=5,
                ),
                ft.VerticalDivider(width=1),
                ft.Container(
                    editor_panel,
                    expand=True,
                    padding=10,
                ),
            ],
            expand=True,
        )
        
        return notes_section
    
    async def select_data_folder(self, e):
        """Handle data folder selection."""
        # Create a file picker for directories
        def on_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.set_data_folder(e.path)
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        # Open directory picker
        file_picker.get_directory_path()
    
    def set_data_folder(self, folder_path: str):
        """Set the data folder and initialize managers."""
        try:
            self.data_folder = folder_path
            # Update data folder display if it exists  
            if hasattr(self, 'data_folder_display') and self.data_folder_display:
                folder_name = os.path.basename(folder_path)
                self.data_folder_display.value = folder_name
            else:
                pass  # data_folder_display not available yet
            
            # Save configuration
            self.save_config()
            
            # Initialize managers
            self.todo_manager = TodoManager(folder_path)
            self.notes_manager = NotesManager(folder_path)
            
            # Refresh UI
            self.refresh_todos()
            # Only refresh notes if the UI components are ready
            if hasattr(self, 'notes_list_view') and self.notes_list_view:
                self.refresh_notes()
            else:
                pass  # Notes UI not ready yet, skipping refresh_notes
            self.update_context_filter()
            self.update_project_filter()
            self.update_filter_counts()
            
            self.page.update()
            
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.show_error("Failed to initialize data folder", str(ex))
    
    def refresh_todos(self):
        """Refresh the todo list based on current filters."""
        if not self.todo_manager:
            return
        
        # Safety check for todo_list_view
        if not hasattr(self, 'todo_list_view') or not self.todo_list_view:
            return
        
        # Get current filter settings
        date_filter = self.date_filter
        context_filter = self.selected_context
        project_filter = self.selected_project
        sort_by = list(self.sort_buttons.selected)[0] if self.sort_buttons and self.sort_buttons.selected else "default"
        
        # Get filtered todos
        if date_filter == "today":
            todos = self.todo_manager.get_todos_due_today()
        elif date_filter == "upcoming":
            todos = self.todo_manager.get_todos_due_upcoming()
        elif date_filter == "someday":
            todos = self.todo_manager.get_todos_someday()
        elif date_filter == "completed":
            todos = self.todo_manager.get_completed_todos()
        else:
            # "all" filter - exclude completed tasks
            todos = [todo for todo in self.todo_manager.items if not todo.completed]
        
        # Filter by context
        if context_filter and context_filter != "all":
            todos = [todo for todo in todos if context_filter in todo.contexts]
        
        # Filter by project
        if project_filter and project_filter != "all":
            todos = [todo for todo in todos if project_filter in todo.projects]
        
        # Sort todos (default: by deadline then priority)
        if sort_by == "priority":
            todos = self.todo_manager.sort_by_priority(todos)
        elif sort_by == "due_date":
            todos = self.todo_manager.sort_by_due_date(todos)
        else:
            # Default sorting: by deadline then priority
            todos = self.sort_by_deadline_then_priority(todos)
        
        # Update list view
        self.todo_list_view.controls.clear()
        for todo in todos:
            todo_card = self.create_todo_card(todo)
            self.todo_list_view.controls.append(todo_card)
        
        self.page.update()
    
    def sort_by_deadline_then_priority(self, todos):
        """Sort todos by deadline first, then by priority."""
        def sort_key(todo):
            # First sort by due date (None values go to the end)
            due_date_key = date.max
            if todo.due_date:
                if isinstance(todo.due_date, str):
                    # Handle case where due_date might be a string
                    try:
                        due_date_key = datetime.strptime(todo.due_date, '%Y-%m-%d').date()
                    except ValueError:
                        due_date_key = date.max
                else:
                    due_date_key = todo.due_date
            
            # Then sort by priority (A=0, B=1, C=2, D=3, E=4, None=5)
            priority_order = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
            priority_key = priority_order.get(todo.priority, 5)
            
            # Completed todos go to the bottom
            completed_key = 1 if todo.completed else 0
            
            return (completed_key, due_date_key, priority_key)
        
        return sorted(todos, key=sort_key)
    
    def create_todo_card(self, todo: TodoItem):
        """Create a beautiful card for a todo item."""
        
        def get_clean_description(description: str) -> str:
            """Extract clean description without projects, contexts, or due dates."""
            import re
            # Remove projects (+project)
            text = re.sub(r'\s*\+\w+', '', description)
            # Remove contexts (@context)
            text = re.sub(r'\s*@\w+', '', text)
            # Remove due dates (due:YYYY-MM-DD)
            text = re.sub(r'\s*due:\d{4}-\d{2}-\d{2}', '', text)
            return text.strip()
        
        # Get clean description (without projects, contexts, or due date)
        clean_description = get_clean_description(todo.description)
        
        # First row: checkbox, trimmed title, edit button
        first_row = ft.Row(
            [
                ft.Checkbox(
                    value=todo.completed,
                    on_change=lambda e, t=todo: self.toggle_todo_completion(t),
                ),
                ft.Container(
                    ft.Text(
                        clean_description,
                        size=14,
                        color=ft.Colors.GREY_600 if todo.completed else ft.Colors.BLACK,
                        style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if todo.completed else None,
                    ),
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_size=16,
                    tooltip="Edit todo",
                    on_click=lambda e, t=todo: self.edit_todo_dialog(t),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        )
        
        # Second row: priority, projects, deadline
        second_row_left_items = []
        due_date_item = None
        
        # Priority (remove "Priority:" label)
        if todo.priority and not todo.completed:
            colors = {
                'A': ft.Colors.RED,
                'B': ft.Colors.ORANGE, 
                'C': ft.Colors.AMBER,
                'D': ft.Colors.GREEN,
                'E': ft.Colors.BLUE,
            }
            second_row_left_items.append(
                ft.Container(
                    ft.Text(f"{todo.priority}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                    bgcolor=colors.get(todo.priority, ft.Colors.GREY),
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=10,
                )
            )
        
        # Projects - create individual tags
        if todo.projects:
            for project in todo.projects:
                second_row_left_items.append(
                    ft.Container(
                        ft.Text(f"+{project}", color=ft.Colors.PURPLE_800, size=12),
                        bgcolor=ft.Colors.PURPLE_50,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=10,
                    )
                )
        
        # Contexts - create individual tags
        if todo.contexts:
            for context in todo.contexts:
                second_row_left_items.append(
                    ft.Container(
                        ft.Text(f"@{context}", color=ft.Colors.GREEN_800, size=12),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                        border_radius=10,
                    )
                )
        
        # Due date (will be positioned on far right)
        if todo.due_date:
            today = date.today()
            if todo.due_date < today:
                due_text = f"Overdue ({(today - todo.due_date).days} days)"
                due_color = ft.Colors.RED
            elif todo.due_date == today:
                due_text = "Today"
                due_color = ft.Colors.ORANGE
            elif todo.due_date == today + timedelta(days=1):
                due_text = "Tomorrow"
                due_color = ft.Colors.ORANGE_300
            else:
                days_diff = (todo.due_date - today).days
                if days_diff <= 5:
                    due_text = f"+{days_diff} days"
                    due_color = ft.Colors.BLUE
                else:
                    due_text = todo.due_date.strftime('%Y-%m-%d')
                    due_color = ft.Colors.BLUE_200  # Lighter blue for distant deadlines
            
            due_date_item = ft.Container(
                ft.Text(due_text, color=ft.Colors.WHITE, size=12),
                bgcolor=due_color,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=10,
            )
        
        # Second row with deadline on far right
        if second_row_left_items or due_date_item:
            second_row = ft.Row(
                [
                    ft.Row(second_row_left_items, spacing=5, wrap=True),
                    due_date_item if due_date_item else ft.Container(),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        else:
            second_row = ft.Container()
        
        # Card container
        return ft.Card(
            ft.Container(
                ft.Column(
                    [first_row, second_row],
                    spacing=5,
                ),
                padding=10,
                on_click=lambda e, t=todo: self.edit_todo_dialog(t),
            ),
            elevation=1,
        )
    
    def refresh_notes(self):
        """Refresh the notes list."""
        if not self.notes_manager:
            return
        
        # Safety check for notes_list_view
        if not hasattr(self, 'notes_list_view') or not self.notes_list_view:
            return
        
        notes = self.notes_manager.get_notes_by_title_sorted()
        
        self.notes_list_view.controls.clear()
        for note in notes:
            # Check if this is the currently selected note using filepath as identifier
            is_selected = self.current_note and self.current_note.filepath == note.filepath
            
            note_card = ft.Card(
                ft.ListTile(
                    title=ft.Text(note.title, weight=ft.FontWeight.BOLD, size=14),
                    subtitle=ft.Text(
                        note.modified_time.strftime("%m/%d/%Y %H:%M") if note.modified_time else "No date",
                        size=12
                    ),
                    on_click=lambda e, n=note: self.select_note(n),
                    content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    selected=is_selected,
                ),
                elevation=2 if is_selected else 1,
                margin=ft.margin.all(2),
                color=ft.Colors.BLUE_50 if is_selected else None,
            )
            self.notes_list_view.controls.append(note_card)
        
        self.page.update()
    
    def select_note(self, note: Note):
        """Select and load a note for preview."""
        # Check for unsaved changes before switching notes
        if self.current_note and self.note_has_unsaved_changes and self.current_note.filepath != note.filepath:
            # Show save dialog before switching
            self.show_save_before_navigation_dialog(
                lambda: self.load_note(note)
            )
            return
        
        self.load_note(note)
    
    def load_note(self, note: Note):
        """Load a note into the editor."""
        self.current_note = note
        self.note_has_unsaved_changes = False
        
        # Update edit content (now tab 1)
        edit_tab = self.note_editor.tabs[1].content
        edit_tab.value = note.content
        
        # Update preview - markdown is now in tab 0, nested in container
        preview_tab = self.note_editor.tabs[0].content
        preview_markdown = preview_tab.controls[0].content  # Container -> Markdown
        preview_markdown.value = note.content or "# Empty Note\n\nStart writing..."
        
        # Switch to preview tab when selecting a note (now tab 0)
        self.note_editor.selected_index = 0
        
        # Update status
        self.update_note_status()
        
        # Refresh the notes list to update highlighting
        self.refresh_notes()
        
        self.page.update()
    
    def update_note_status(self):
        """Update the note status indicator."""
        if not self.current_note:
            self.note_status_text.value = ""
            self.save_button.icon_color = None
        elif self.note_has_unsaved_changes:
            self.note_status_text.value = "● Unsaved changes"
            self.note_status_text.color = ft.Colors.ORANGE_600
            self.save_button.icon_color = ft.Colors.ORANGE_600
        else:
            self.note_status_text.value = "✓ Saved"
            self.note_status_text.color = ft.Colors.GREEN_600
            self.save_button.icon_color = None
        self.page.update()
    
    # Additional methods for dialogs, filters, etc.
    def get_current_date_filter(self):
        """Get the currently selected date filter."""
        for filter_type, button in self.todo_filter_buttons.items():
            if button.style and button.style.bgcolor == ft.Colors.BLUE_100:
                return filter_type
        return "all"
    
    def set_filter(self, filter_type: str, filter_value: str):
        """Unified method to set any filter type and refresh."""
        if filter_type == "date":
            # Special case: if setting date filter to "all", also reset other filters
            if filter_value == "all":
                self.selected_context = "all"
                self.selected_project = "all"
                # Update context and project filter buttons to reflect "all" selection
                self.update_filter_counts("context")
                self.update_filter_counts("project")
                # Update button styles for context filters
                for key, button in self.context_filter_buttons.items():
                    selected = key == "all"
                    button.style = ft.ButtonStyle(
                        bgcolor=ft.Colors.GREEN_100 if selected else None,
                        color=ft.Colors.GREEN_900 if selected else ft.Colors.GREY_800,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    )
                # Update button styles for project filters  
                for key, button in self.project_filter_buttons.items():
                    selected = key == "all"
                    button.style = ft.ButtonStyle(
                        bgcolor=ft.Colors.PURPLE_100 if selected else None,
                        color=ft.Colors.PURPLE_900 if selected else ft.Colors.GREY_800,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    )
            
            # Update date filter
            for key, button in self.todo_filter_buttons.items():
                selected = key == filter_value
                count = self.count_todos_by_date_filter(key)
                
                # Update the button content (count is now in a Container with Text inside)
                button.content.controls[1].content.value = str(count)
                button.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.BLUE_100 if selected else None,
                    color=ft.Colors.BLUE_800 if selected else ft.Colors.GREY_800,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                )
            self.date_filter = filter_value
            
        elif filter_type == "context":
            # Update context filter
            for key, button in self.context_filter_buttons.items():
                selected = key == filter_value
                count = self.count_todos_by_context(key)
                
                # Update the button content (count is now in a Container with Text inside)
                button.content.controls[1].content.value = str(count)
                button.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN_100 if selected else None,
                    color=ft.Colors.GREEN_900 if selected else ft.Colors.GREY_800,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                )
            self.selected_context = filter_value
            
        elif filter_type == "project":
            # Update project filter
            for key, button in self.project_filter_buttons.items():
                selected = key == filter_value
                count = self.count_todos_by_project(key)
                
                # Update the button content (count is now in a Container with Text inside)
                button.content.controls[1].content.value = str(count)
                button.style = ft.ButtonStyle(
                    bgcolor=ft.Colors.PURPLE_100 if selected else None,
                    color=ft.Colors.PURPLE_900 if selected else ft.Colors.GREY_800,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                )
            self.selected_project = filter_value
        
        # Refresh todos for all filter types
        self.refresh_todos()
        self.page.update()

    def set_date_filter(self, filter_type: str):
        """Set the date filter and refresh."""
        self.set_filter("date", filter_type)

    def set_context_filter(self, context: str):
        """Set the context filter and refresh."""
        self.set_filter("context", context)

    def set_project_filter(self, project: str):
        """Set the project filter and refresh."""
        self.set_filter("project", project)
    
    def count_todos_by_date_filter(self, filter_type: str) -> int:
        """Count todos matching a date filter."""
        if not self.todo_manager:
            return 0
        
        if filter_type == "today":
            return len(self.todo_manager.get_todos_due_today())
        elif filter_type == "upcoming":
            return len(self.todo_manager.get_todos_due_upcoming())
        elif filter_type == "someday":
            return len(self.todo_manager.get_todos_someday())
        elif filter_type == "completed":
            return len(self.todo_manager.get_completed_todos())
        else:  # "all"
            return len([todo for todo in self.todo_manager.items if not todo.completed])
    
    def count_todos_by_context(self, context: str) -> int:
        """Count todos matching a context filter."""
        if not self.todo_manager:
            return 0
        
        if context == "all":
            return len([todo for todo in self.todo_manager.items if not todo.completed])
        else:
            return len([todo for todo in self.todo_manager.items if not todo.completed and context in todo.contexts])
    
    def count_todos_by_project(self, project: str) -> int:
        """Count todos matching a project filter."""
        if not self.todo_manager:
            return 0
        
        if project == "all":
            return len([todo for todo in self.todo_manager.items if not todo.completed])
        else:
            return len([todo for todo in self.todo_manager.items if not todo.completed and project in todo.projects])
    
    def update_context_filter(self):
        """Update the context filter buttons."""
        if not self.todo_manager:
            return
        
        # Safety check for UI components
        if not hasattr(self, 'context_filter_container') or not self.context_filter_container:
            return
        
        try:
            self.context_filter_buttons.clear()
            self.context_filter_container.controls.clear()
            
            # Add "All Contexts" button
            all_button = self.create_context_filter_button("all", "All", self.selected_context == "all")
            self.context_filter_container.controls.append(all_button)
            
            # Add buttons for each context
            contexts = self.todo_manager.get_all_contexts()
            for context in contexts:
                button = self.create_context_filter_button(context, context, self.selected_context == context)
                self.context_filter_container.controls.append(button)
            
            # Update all filter counts
            self.update_filter_counts()
            self.page.update()
        except Exception as ex:
            pass  # Silently handle context filter update errors
    
    def update_project_filter(self):
        """Update the project filter buttons."""
        if not self.todo_manager:
            return
        
        # Safety check for UI components
        if not hasattr(self, 'project_filter_container') or not self.project_filter_container:
            return
        
        try:
            self.project_filter_buttons.clear()
            self.project_filter_container.controls.clear()
            
            # Add "All Projects" button
            all_button = self.create_project_filter_button("all", "All", self.selected_project == "all")
            self.project_filter_container.controls.append(all_button)
            
            # Add buttons for each project
            projects = self.todo_manager.get_all_projects()
            for project in projects:
                button = self.create_project_filter_button(project, project, self.selected_project == project)
                self.project_filter_container.controls.append(button)
            
            # Update all filter counts
            self.update_filter_counts()
            self.page.update()
        except Exception as ex:
            pass  # Silently handle project filter update errors
    
    def update_filter_counts(self, filter_type: str = "all"):
        """Update the counts on filter buttons."""
        try:
            if filter_type in ["all", "date"]:
                for key, button in self.todo_filter_buttons.items():
                    if hasattr(button, 'content') and button.content and len(button.content.controls) > 1:
                        count = self.count_todos_by_date_filter(key)
                        # The count is now in a Container with a Text widget inside
                        button.content.controls[1].content.value = str(count)
            
            if filter_type in ["all", "context"]:
                for key, button in self.context_filter_buttons.items():
                    if hasattr(button, 'content') and button.content and len(button.content.controls) > 1:
                        count = self.count_todos_by_context(key)
                        # The count is now in a Container with a Text widget inside
                        button.content.controls[1].content.value = str(count)
            
            if filter_type in ["all", "project"]:
                for key, button in self.project_filter_buttons.items():
                    if hasattr(button, 'content') and button.content and len(button.content.controls) > 1:
                        count = self.count_todos_by_project(key)
                        # The count is now in a Container with a Text widget inside
                        button.content.controls[1].content.value = str(count)
        except Exception as ex:
            pass  # Silently handle filter count update errors

    def update_date_filter_counts(self):
        """Update the counts on date filter buttons."""
        self.update_filter_counts("date")
    
    def toggle_todo_completion(self, todo: TodoItem):
        """Toggle todo completion status."""
        if self.todo_manager:
            todo.toggle_completion()
            self.todo_manager.update_todo(todo)
            self.refresh_todos()
    
    def search_notes(self, e):
        """Search notes by query."""
        if not self.notes_manager:
            return
        
        query = e.control.value
        if query:
            notes = self.notes_manager.search_notes(query)
        else:
            notes = self.notes_manager.get_notes_by_title_sorted()
        
        # Update notes list (simplified for now)
        self.refresh_notes()
    
    def on_note_content_changed(self, e):
        """Update preview when note content changes."""
        if self.current_note:
            # Mark as having unsaved changes
            self.note_has_unsaved_changes = True
            self.update_note_status()
            
            # Update preview tab with new content
            preview_tab = self.note_editor.tabs[0].content
            preview_markdown = preview_tab.controls[0].content
            preview_markdown.value = e.control.value or "# Empty Note"
            
            self.page.update()
    
    def save_current_note(self, e):
        """Save the current note."""
        if self.current_note:
            # Get content from the edit tab (tab 1)
            edit_tab = self.note_editor.tabs[1].content
            content = edit_tab.value
            
            # Update note content and title, then save
            self.current_note.update_content(content)
            self.current_note.save()
            
            # Clear unsaved changes flag and update status
            self.note_has_unsaved_changes = False
            self.update_note_status()
            
            # Also update the preview tab
            preview_tab = self.note_editor.tabs[0].content
            preview_markdown = preview_tab.controls[0].content
            preview_markdown.value = content or "# Empty Note\n\nStart writing..."
            
            # Refresh the notes list to show updated title
            self.refresh_notes()
            self.page.update()
    
    def show_save_before_navigation_dialog(self, continue_action):
        """Show dialog asking user to save before navigation."""
        def save_and_continue(e):
            self.save_current_note(None)
            self.page.close(dialog)
            self.current_dialog = None
            continue_action()
        
        def continue_without_saving(e):
            # Clear unsaved changes flag and continue
            self.note_has_unsaved_changes = False
            self.page.close(dialog)
            self.current_dialog = None
            continue_action()
        
        def cancel_navigation(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Unsaved Changes"),
            content=ft.Text(f"You have unsaved changes in '{self.current_note.title}'.\n\nDo you want to save before continuing?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_navigation),
                ft.TextButton("Don't Save", on_click=continue_without_saving),
                ft.ElevatedButton("Save & Continue", on_click=save_and_continue),
            ],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def show_save_on_close_dialog(self):
        """Show dialog asking user to save before closing."""
        def save_and_close(e):
            self.save_current_note(None)
            self.page.close(dialog)
            self.current_dialog = None
            self.page.window_close()
        
        def close_without_saving(e):
            self.page.close(dialog)
            self.current_dialog = None
            self.page.window_close()
        
        def cancel_close(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Unsaved Changes"),
            content=ft.Text(f"You have unsaved changes in '{self.current_note.title}'.\n\nDo you want to save before closing?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_close),
                ft.TextButton("Don't Save", on_click=close_without_saving),
                ft.ElevatedButton("Save & Close", on_click=save_and_close),
            ],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def delete_current_note(self, e):
        """Delete the current note with confirmation."""
        if not self.current_note:
            return
            
        def close_dialog(e):
            self.page.close(confirm_dialog)
            self.current_dialog = None
        
        def confirm_delete(e):
            if self.notes_manager:
                self.notes_manager.delete_note(self.current_note)
                self.current_note = None
                self.refresh_notes()
                
                # Clear edit tab (now tab 1)
                edit_tab = self.note_editor.tabs[1].content
                edit_tab.value = ""
                
                # Clear preview - markdown is now in tab 0, nested in container
                preview_tab = self.note_editor.tabs[0].content
                preview_markdown = preview_tab.controls[0].content
                preview_markdown.value = "Select a note to preview..."
                
                self.page.update()
            close_dialog(e)
        
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete the note?\n\n'{self.current_note.title}'"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", on_click=confirm_delete, color=ft.Colors.RED),
            ],
        )
        
        self.current_dialog = confirm_dialog
        self.page.open(confirm_dialog)
    
    def add_todo_dialog(self, e):
        """Show dialog to add a new todo."""
        
        def close_dialog(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        def save_todo(e):
            description = description_field.value.strip()
            
            if not self.todo_manager:
                self.show_error("Error", "Please select a data folder first")
                return
                
            if description:
                # Create todo with raw description first - this will auto-parse todo.txt format
                todo = self.todo_manager.add_todo(description)
                
                # Only override parsed values if form fields are explicitly set
                # This allows users to use either the description format OR the form fields
                
                # Set priority from dropdown only if it's not "none" AND not already parsed
                if priority_dropdown.value != "none" and not todo.priority:
                    todo.set_priority(priority_dropdown.value)
                
                # Set due date from date picker only if checkbox is checked AND not already parsed
                if due_date_checkbox.value and date_picker.value and not todo.due_date:
                    todo.set_due_date(date_picker.value)
                
                # Add projects from field - add any that aren't already present
                if projects_field.value:
                    for project in projects_field.value.split(','):
                        project = project.strip()
                        if project and project not in todo.projects:
                            todo.add_project(project)
                
                # Add contexts from field - add any that aren't already present
                if contexts_field.value:
                    for context in contexts_field.value.split(','):
                        context = context.strip()
                        if context and context not in todo.contexts:
                            todo.add_context(context)
                
                # Save the updated todo
                self.todo_manager.save_todos()
                self.refresh_todos()
                self.update_context_filter()
                self.update_project_filter()
            
            close_dialog(e)
        
        def on_due_date_checkbox_change(e):
            due_date_button.disabled = not e.control.value
            self.page.update()
        
        def open_date_picker(e):
            self.page.open(date_picker)
        
        def on_date_picked(e):
            due_date_button.text = f"Due: {date_picker.value.strftime('%Y-%m-%d')}"
            self.page.update()
        
        # Dialog fields
        description_field = ft.TextField(
            label="Description*", 
            hint_text="e.g., (A) Call dentist +health @phone due:2024-08-30",
            autofocus=True,
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_submit=save_todo,
        )
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("none", "None"),
                ft.dropdown.Option("A", "A (Highest)"),
                ft.dropdown.Option("B", "B (High)"),
                ft.dropdown.Option("C", "C (Medium)"),
                ft.dropdown.Option("D", "D (Low)"),
                ft.dropdown.Option("E", "E (Lowest)"),
            ],
            value="none",
        )
        due_date_checkbox = ft.Checkbox(
            label="Set due date",
            on_change=on_due_date_checkbox_change
        )
        
        # Date picker and button
        date_picker = ft.DatePicker(
            on_change=on_date_picked,
            first_date=date.today(),
            last_date=date(2030, 12, 31),
        )
        
        due_date_button = ft.ElevatedButton(
            text="Select Date",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=open_date_picker,
            disabled=True
        )
        
        projects_field = ft.TextField(
            label="Projects (comma separated)", 
            hint_text="e.g., Work, Personal, Health"
        )
        contexts_field = ft.TextField(
            label="Contexts (comma separated)", 
            hint_text="e.g., home, office, computer"
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New Todo"),
            content=ft.Column([
                description_field,
                ft.Text(
                    "💡 Tip: Use todo.txt format in description: (A) priority, +project, @context, due:YYYY-MM-DD",
                    size=12,
                    color=ft.Colors.GREY_600,
                    italic=True,
                ),
                ft.Divider(),
                ft.Text("Or use the fields below:", size=12, color=ft.Colors.GREY_600),
                priority_dropdown,
                ft.Row([due_date_checkbox, due_date_button]),
                ft.Divider(),
                projects_field,
                contexts_field,
            ], height=450, scroll=ft.ScrollMode.AUTO, width=500),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Add Todo", on_click=save_todo),
            ],
        )
        
        # Add the date picker to the page overlay
        self.page.overlay.append(date_picker)
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def new_note_with_check(self, e):
        """Create new note with unsaved changes check."""
        if self.current_note and self.note_has_unsaved_changes:
            self.show_save_before_navigation_dialog(
                lambda: self.new_note_dialog(None)
            )
        else:
            self.new_note_dialog(e)
    
    def new_note_dialog(self, e):
        """Show dialog to create a new note."""
        def close_dialog(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        def create_note(e):
            title = title_field.value.strip()
            if title and self.notes_manager:
                note = self.notes_manager.create_note(title)
                self.refresh_notes()
                self.load_note(note)  # Use load_note directly since no unsaved changes
                # Switch to edit mode (tab 1) after creating the note
                self.note_editor.selected_index = 1
                self.page.update()
                
                # Focus on the edit text field
                edit_tab = self.note_editor.tabs[1].content
                edit_tab.focus()
                self.page.update()
            close_dialog(e)
        
        title_field = ft.TextField(
            label="Note Title*", 
            autofocus=True,
            on_submit=create_note,
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Note"),
            content=title_field,
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Create", on_click=create_note),
            ],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def show_error(self, title: str, message: str):
        """Show an error dialog."""
        def close_dialog(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=ft.Colors.RED),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=close_dialog)],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def show_welcome_message(self):
        """Show welcome message on first run."""
        def close_dialog(e):
            self.page.close(dialog)
            self.current_dialog = None
            self.select_data_folder(e)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Welcome to DoNotePad! 🎉"),
            content=ft.Column([
                ft.Text("A beautiful, lightweight productivity app for managing todos and notes."),
                ft.Text(""),
                ft.Text("Features:"),
                ft.Text("• Todo.txt format support with priorities and due dates"),
                ft.Text("• Markdown notes with live preview"),
                ft.Text("• Beautiful Material Design interface"),
                ft.Text("• Plain text storage (no database)"),
                ft.Text(""),
                ft.Text("Let's get started by selecting a data folder."),
            ], height=250),
            actions=[ft.ElevatedButton("Select Data Folder", on_click=close_dialog)],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)

    def edit_todo_dialog(self, todo: TodoItem):
        """Show dialog to edit an existing todo."""
        def close_dialog(e):
            # Clean up the date picker from overlay
            if edit_date_picker in self.page.overlay:
                self.page.overlay.remove(edit_date_picker)
            self.page.close(dialog)
            self.current_dialog = None
        
        def delete_todo(e):
            # Show confirmation dialog for delete
            def confirm_delete(e):
                if self.todo_manager:
                    self.todo_manager.remove_todo(todo)
                    self.refresh_todos()
                    self.update_context_filter()
                    self.update_project_filter()
                # Close both confirmation dialog and main edit dialog
                self.page.close(confirm_dialog)
                close_dialog(e)
            
            def cancel_delete(e):
                self.page.close(confirm_dialog)
            
            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete this todo?\n\n'{todo.description}'"),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.ElevatedButton("Delete", on_click=confirm_delete, color=ft.Colors.RED),
                ],
            )
            
            self.page.open(confirm_dialog)
        
        def save_todo(e):
            description = description_field.value.strip()
            if description and self.todo_manager:
                # Get clean description without projects, contexts, due dates
                clean_description = get_clean_description(description)
                
                # Start fresh with clean description
                todo.description = clean_description
                todo.projects.clear()
                todo.contexts.clear()
                
                # Set priority
                if priority_dropdown.value != "none":
                    todo.set_priority(priority_dropdown.value)
                else:
                    todo.priority = None
                
                # Set due date from date picker
                if due_date_checkbox.value and edit_date_picker.value:
                    todo.set_due_date(edit_date_picker.value)
                else:
                    todo.set_due_date(None)
                
                # Add projects using proper method to update description
                if projects_field.value:
                    for project in projects_field.value.split(','):
                        project = project.strip()
                        if project:
                            todo.add_project(project)
                
                # Add contexts using proper method to update description
                if contexts_field.value:
                    for context in contexts_field.value.split(','):
                        context = context.strip()
                        if context:
                            todo.add_context(context)
                
                self.todo_manager.save_todos()
                self.refresh_todos()
                self.update_context_filter()
                self.update_project_filter()
            
            close_dialog(e)
        
        def on_due_date_checkbox_change(e):
            edit_due_date_button.disabled = not e.control.value
            self.page.update()
        
        def open_edit_date_picker(e):
            self.page.open(edit_date_picker)
        
        def on_edit_date_picked(e):
            edit_due_date_button.text = f"Due: {edit_date_picker.value.strftime('%Y-%m-%d')}"
            self.page.update()
        
        def get_clean_description(description: str) -> str:
            """Extract clean description without projects, contexts, or due dates."""
            import re
            # Remove projects (+project)
            text = re.sub(r'\s*\+\w+', '', description)
            # Remove contexts (@context)
            text = re.sub(r'\s*@\w+', '', text)
            # Remove due dates (due:YYYY-MM-DD)
            text = re.sub(r'\s*due:\d{4}-\d{2}-\d{2}', '', text)
            return text.strip()
        
        # Get clean description (without projects, contexts, or due date)
        trimmed_description = get_clean_description(todo.description)
        
        # Pre-populate dialog fields with current todo data
        description_field = ft.TextField(
            label="Description*", 
            value=trimmed_description, 
            autofocus=True,
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        
        priority_dropdown = ft.Dropdown(
            label="Priority",
            options=[
                ft.dropdown.Option("none", "None"),
                ft.dropdown.Option("A", "A (Highest)"),
                ft.dropdown.Option("B", "B (High)"),
                ft.dropdown.Option("C", "C (Medium)"),
                ft.dropdown.Option("D", "D (Low)"),
                ft.dropdown.Option("E", "E (Lowest)"),
            ],
            value=todo.priority if todo.priority else "none",
        )
        
        due_date_checkbox = ft.Checkbox(
            label="Set due date", 
            value=bool(todo.due_date),
            on_change=on_due_date_checkbox_change
        )
        
        # Date picker and button for edit dialog
        edit_date_picker = ft.DatePicker(
            on_change=on_edit_date_picked,
            first_date=date.today(),
            last_date=date(2030, 12, 31),
            value=todo.due_date if todo.due_date else date.today(),
        )
        
        edit_due_date_button = ft.ElevatedButton(
            text=f"Due: {todo.due_date.strftime('%Y-%m-%d')}" if todo.due_date else "Select Date",
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=open_edit_date_picker,
            disabled=not bool(todo.due_date)
        )
        
        projects_field = ft.TextField(
            label="Projects (comma-separated)",
            value=", ".join(todo.projects) if todo.projects else "",
            hint_text="e.g., Work, Personal, Health"
        )
        
        contexts_field = ft.TextField(
            label="Contexts (comma-separated)",
            value=", ".join(todo.contexts) if todo.contexts else "",
            hint_text="e.g., home, office, computer"
        )
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Todo"),
            content=ft.Column([
                description_field,
                ft.Divider(),
                priority_dropdown,
                ft.Row([due_date_checkbox, edit_due_date_button]),
                ft.Divider(),
                projects_field,
                contexts_field,
            ], height=500, scroll=ft.ScrollMode.AUTO, width=600),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", on_click=delete_todo, color=ft.Colors.RED),
                ft.ElevatedButton("Save Changes", on_click=save_todo),
            ],
        )
        
        # Add the date picker to the page overlay
        self.page.overlay.append(edit_date_picker)
        self.current_dialog = dialog
        self.page.open(dialog)
    
    def delete_note(self, note: Note):
        """Delete a note with confirmation."""
        def close_dialog(e):
            self.page.close(dialog)
            self.current_dialog = None
        
        def confirm_delete(e):
            if self.notes_manager:
                self.notes_manager.delete_note(note)
                if self.current_note and self.current_note.title == note.title:
                    self.current_note = None
                    # Clear edit tab (now tab 1)
                    edit_tab = self.note_editor.tabs[1].content
                    edit_tab.value = ""
                    # Clear preview - markdown is now in tab 0, nested in container
                    preview_tab = self.note_editor.tabs[0].content
                    preview_markdown = preview_tab.controls[0].content
                    preview_markdown.value = "# No Note Selected\n\nSelect a note to edit or create a new one."
                self.refresh_notes()
            close_dialog(e)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete the note?\n\n'{note.title}'"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton("Delete", on_click=confirm_delete, color=ft.Colors.RED),
            ],
        )
        
        self.current_dialog = dialog
        self.page.open(dialog)


def main(page: ft.Page):
    """Main entry point for Flet app."""
    app = DoNotePadApp(page)


if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--version', '-v']:
            print("DoNotePad v1.0.1")
            print("A beautiful, lightweight productivity app for managing todos and notes")
            sys.exit(0)
        elif sys.argv[1] in ['--help', '-h']:
            print("DoNotePad v1.0.1")
            print("A beautiful, lightweight productivity app for managing todos and notes")
            print("")
            print("Usage: donotepad [options]")
            print("")
            print("Options:")
            print("  -h, --help     Show this help message and exit")
            print("  -v, --version  Show version information and exit")
            print("")
            print("Features:")
            print("  • Todo.txt format support with priorities and due dates")
            print("  • Markdown notes with live preview")
            print("  • Beautiful Material Design interface")
            print("  • Plain text storage (no database)")
            print("  • Keyboard shortcuts for power users")
            sys.exit(0)
    
    ft.app(target=main)
