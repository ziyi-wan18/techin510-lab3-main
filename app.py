import sqlite3
import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp

# Database connection
con = sqlite3.connect("todoapp.sqlite", isolation_level=None)
cur = con.cursor()

# Create tasks table if it doesn't exist
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        is_done BOOLEAN
    )
    """
)

# Task model
class Task(BaseModel):
    name: str
    description: str
    is_done: bool

# Function to toggle task status
def toggle_is_done(is_done, row):
    cur.execute(
        """
        UPDATE tasks SET is_done = ? WHERE id = ?
        """,
        (is_done, row[0]),
    )

# Function to delete a task
def delete_task(task_id):
    cur.execute(
        """
        DELETE FROM tasks WHERE id = ?
        """,
        (task_id,)
    )

# Main function to render the app
def main():
    st.title("Todo App")

    # Task creation form
    data = sp.pydantic_form(key="task_form", model=Task)
    if data:
        cur.execute(
            """
            INSERT INTO tasks (name, description, is_done) VALUES (?, ?, ?)
            """,
            (data.name, data.description, data.is_done),
        )

    # Search and filter features
    search_query = st.text_input("Search tasks")
    filter_status = st.selectbox("Filter by status", ["All", "Done", "Not Done"])

    # Fetch tasks based on search and filter
    query = "SELECT * FROM tasks WHERE name LIKE ?"
    if filter_status == "Done":
        query += " AND is_done = 1"
    elif filter_status == "Not Done":
        query += " AND is_done = 0"
    data = cur.execute(query, ('%' + search_query + '%',)).fetchall()

    # Display tasks
    for row in data:
        cols = st.columns(4)
        done_label = "Done" if row[3] else "Not Done"
        cols[0].checkbox(done_label, row[3], key=row[0], on_change=toggle_is_done, args=(not row[3], row))
        cols[1].write(row[1])
        cols[2].write(row[2])
        cols[3].button("Delete", key=f"delete_{row[0]}", on_click=delete_task, args=(row[0],))

main()
