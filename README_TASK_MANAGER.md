# Task Manager

A simple yet powerful task management application with a graphical user interface built using Python and Tkinter.

## Features

- **Add Tasks**: Create new tasks with title, description, due date, and priority level
- **Edit Tasks**: Modify existing task details
- **Delete Tasks**: Remove tasks that are no longer needed
- **Mark as Complete**: Toggle task completion status
- **Filter Tasks**: View all, pending, completed, due today, or overdue tasks
- **Sort Tasks**: Organize by due date, priority, or creation date
- **View Details**: See complete task information
- **Data Persistence**: Automatically saves tasks between sessions

## Screenshots

(Screenshots would be added here)

## Requirements

- Python 3.6 or higher
- Tkinter (usually comes with Python)

## How to Run

```bash
python 19_task_manager.py
```

## Usage Guide

1. **Adding a Task**:
   - Click the "Add Task" button or use File > New Task
   - Enter task details in the dialog
   - Click "Save"

2. **Managing Tasks**:
   - Select a task from the list to perform actions on it
   - Use the buttons at the top to edit, delete, or mark tasks as complete
   - Double-click on a task to view its full details

3. **Filtering and Sorting**:
   - Use the dropdown menus to filter tasks by status
   - Sort tasks by due date, priority, or creation date
   - The status bar shows task statistics

## Data Storage

Tasks are saved in a `tasks.json` file in the same directory as the application. This file is automatically loaded when the application starts and updated when tasks change.

## Task Properties

- **Title**: Short name for the task (required)
- **Description**: Detailed information about the task
- **Due Date**: When the task should be completed (format: YYYY-MM-DD)
- **Priority**: High, Medium, or Low
- **Status**: Pending, Completed, or Overdue (calculated automatically)
- **Created Date**: When the task was created (set automatically)

## Future Improvements

- Task categories/tags
- Recurring tasks
- Notifications for upcoming due dates
- Search functionality
- Export/import tasks
- Multiple task lists/projects 