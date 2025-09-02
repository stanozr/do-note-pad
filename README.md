# DoNotePad

A lightweight productivity app for managing to-do lists and taking Markdown notes, built with Flet for a modern Material Design interface.

## Features

### To-Do List Management

- **Todo.txt format support**: Compatible with the standard todo.txt syntax
- **Priority management**: Set priorities (A-Z) for tasks with color coding
- **Project and context organization**: Use +project and @context tags with visual badges
- **Due date tracking**: Set and track due dates with color-coded warnings
- **Filtering options**: Filter by date (today, upcoming, someday, completed) and projects
- **Sorting capabilities**: Sort by priority or due date
- **Beautiful todo cards**: Modern Material Design cards with visual indicators

### Notes Management

- **Markdown support**: Create and edit notes in Markdown format
- **Quick search**: Search across all notes by title and content
- **File-based storage**: Notes stored as individual .md files
- **Tabbed interface**: Clean separation between todos and notes

### User Interface

- **Material Design**: Modern, beautiful interface with Flet framework
- **Responsive layout**: Optimized for desktop usage
- **Tabbed navigation**: Clean separation of todos and notes
- **Data folder selection**: Easy folder picker for your data location
- **Color-coded priorities**: Visual priority indicators (A=Red, B=Orange, C=Amber, D=Green, E=Blue)
- **Web-based UI**: Runs in browser for consistent cross-platform experience

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux desktop environment

### Setup

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
./run.sh
```

The application will start and be available at `http://localhost:8550`

```

## Usage

### First Run

1. On first launch, click "Select Folder" at the bottom to choose your data folder
2. This folder will contain your `todo.txt` file and notes as `.md` files
3. All data is stored as plain text files that can be edited externally

### Todo Management

- **Add todos**: Click "Add Todo" button to create new tasks
- **Edit todos**: Click the edit icon on any todo card
- **Complete todos**: Check the checkbox to toggle completion
- **Filter tasks**: Use the filter buttons to view by date (All, Today, Upcoming, Someday, Completed)
- **Sort tasks**: Use the sort dropdown to sort by priority or due date
- **Filter by project**: Select a specific project from the dropdown

### Notes Management

- **Create notes**: Click "New Note" and provide a title
- **Edit notes**: Click on any note card to edit
- **Search notes**: Use the search box to find notes by title or content
- **Delete notes**: Use the delete button on note cards

### Data Folder Selection

- The data folder selector is located at the bottom of the application
- Click "Select Folder" to choose where your todos and notes are stored
- **The application remembers your folder selection** and will automatically load it on restart
- The current folder path is displayed for reference

## Data Storage

### File Structure

```

your-data-folder/
├── todo.txt # Todo list in todo.txt format
├── note1.md # Individual note files
├── note2.md
└── ...

```

### Todo.txt Syntax

The application supports the standard todo.txt format:

- `(A) Call Mom +Family @home due:2024-08-27`
- `x 2024-08-25 (B) Christmas shopping +Personal @errands`

Priority levels are color-coded:
- **A**: Red (Highest priority)
- **B**: Orange
- **C**: Amber
- **D**: Green
- **E**: Blue (Lowest priority)

### External Editing

All files can be edited with external tools:

- Edit `todo.txt` with any text editor
- Edit `.md` files with any Markdown editor
- Changes will be reflected when you refresh or restart the application

## Technical Details

- **Language**: Python 3
- **GUI Framework**: Flet (Flutter for Python)
- **Storage**: Plain text files only (no database)
- **Dependencies**: Flet, python-dateutil
- **Interface**: Web-based Material Design UI
- **Configuration**: Stored in `~/.donotepad_config.json`

## System Requirements

- Python 3.8 or higher
- libmpv system library for multimedia support
- Modern web browser (interface runs at http://localhost:8550)

## Configuration

The application stores its configuration in `~/.donotepad_config.json`, which includes:
- **Data folder path**: Automatically remembered between sessions
- Settings are automatically saved when changed

### Note Saving

- Notes show "● Unsaved changes" when modified
- Save manually with Ctrl+S or the save button
- **Save on close**: When closing the app with unsaved changes, you'll be prompted to save

## License

This project is open source. Feel free to use, modify, and distribute as needed.
```
