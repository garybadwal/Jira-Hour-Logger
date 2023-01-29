from datetime import datetime, time
import os


import tkinter as tk
from tkinter import ttk
from jira import JIRA


from config import API_TOKEN, EMAIL_ID, SERVER_LINK

cron_command = "0 18 * * 1-5 cd {} && python3 {}/main.py".format(os.getcwd(), os.getcwd())

jira = JIRA(basic_auth=(f"{EMAIL_ID}", f"{API_TOKEN}"), options={'server': f'{SERVER_LINK}'})

def log_hours():
    try:
        # get the selected project
        project_key = eval(project_var.get())[0]
        # get the selected issue
        issue_key = eval(issue_var.get())[0]
        # set the amount of hours to log
        hours = 9
        # get the comment from the text field
        comment = comment_var.get("1.0", "end-1c")
        now = datetime.now()
        # Set the time to 9 AM
        morning_time = time(hour=9,minute=0,second=0)
        # combine the date and time
        start_time = datetime.combine(now, morning_time)
        jira.add_worklog(issue_key,timeSpent='9h',started=start_time,comment=comment)
        success_label.config(text=f"Work Logged Successfully for Issue - : {project_key}")
    except Exception as e:
        success_label.config(text=f"An error occurred: {e}")

def get_project():
    project_list = []
    try:
        # Get the list of all projects in Jira
        projects = jira.projects()
        project_list = [(project.key, project.name) for project in projects]
    except Exception as e:
        success_label.config(text=f"An error occurred: {e}")
    
    return project_list

def get_issues(project_key):
    issue_list = []
    try:
        issues = jira.search_issues(f'project = {project_key} and assignee = currentUser() and status = "In Progress"')
        issue_list = [(issue.id, issue.key, issue.get_field("summary")) for issue in issues]
    except Exception as e:
        success_label.config(text=f"An error occurred: {e}")
    return issue_list

def create_cron_job():
    with open("/tmp/my_cron.txt", "w") as f:
        f.write(cron_command)
    os.system("crontab /tmp/my_cron.txt")

def set_cron_job():
    create_cron_job()
    success_label.config(text="Cron job set successfully")

def remove_cron_job():
    os.system("crontab -r")
    success_label.config(text="Cron job removed successfully")

root = tk.Tk()
root.title("Jira Hour Logger")

# Create a label to display the success message
success_label = ttk.Label(root, text="")
success_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Create a label for the project selection
project_label = ttk.Label(root, text="Select a Project:")
project_label.grid(row=0, column=0, padx=10, pady=10)

# Create a variable to store the selected project
project_var = tk.StringVar()

# Create a dropdown menu for the projects
project_dropdown = ttk.OptionMenu(root, project_var, *get_project())
project_dropdown.grid(row=0, column=1, padx=10, pady=10)

# Create a label for the issue selection
issue_label = ttk.Label(root, text="Select an Issue:")
issue_label.grid(row=1, column=0, padx=10, pady=10)

# Create a variable to store the selected issue
issue_var = tk.StringVar()

# Create a function to update the issues dropdown when a project is selected
def select_project():
    try:
        issue_dropdown.destroy()
    except:
        pass
    issues = get_issues(eval(project_var.get())[0])
    issue_dropdown = ttk.OptionMenu(root, issue_var, *issues)
    issue_dropdown.grid(row=1, column=1, padx=10, pady=10)

# Create a button to select the project
select_button = ttk.Button(root, text="Select Project", command=select_project)
select_button.grid(row=0, column=2, padx=10, pady=10)

# Create a label for the comment text field
comment_label = ttk.Label(root, text="Enter a comment:")
comment_label.grid(row=2, column=0, padx=10, pady=10)

# Create a text field for the comment
comment_var = tk.Text(root, height=10, width=40)
comment_var.grid(row=2, column=1, padx=10, pady=10)

# Create a button to log the hours
log_button = ttk.Button(root, text="Log Hours", command=log_hours)
log_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


set_cron_button = ttk.Button(root, text="Set Cron Job", command=set_cron_job)
set_cron_button.grid(row=1, column=2, padx=10, pady=10)

remove_cron_button = ttk.Button(root, text="Remove Cron Job", command=remove_cron_job)
remove_cron_button.grid(row=2, column=2, padx=10, pady=10)

root.mainloop()
