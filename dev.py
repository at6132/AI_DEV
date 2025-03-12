import os
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from github import Github
from agents import Agent, Runner, WebSearchTool, ComputerTool, function_tool
from vector_store import save_to_project, delete_file, search_file  # Import FAISS functions

# OpenAI API Key
OPENAI_API_KEY = "your-new-api-key-here"

# GitHub Credentials
GITHUB_ACCESS_TOKEN = "your-github-personal-access-token"
GITHUB_REPO_NAME = "your-username/your-repo"

# AI Workspace (Logs, AI-generated files)
AI_DIRECTORY = "AI"
os.makedirs(AI_DIRECTORY, exist_ok=True)

# GUI Setup
root = tk.Tk()
root.title("AI Multi-Agent Development System")
log_text = scrolledtext.ScrolledText(root, width=100, height=30)
log_text.pack()

def log_message(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)
    root.update_idletasks()

# GitHub Integration Functions
def create_github_branch(branch_name):
    g = Github(GITHUB_ACCESS_TOKEN)
    repo = g.get_repo(GITHUB_REPO_NAME)
    main_branch = repo.get_branch("main")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
    log_message(f"[GitHub] Created new branch: {branch_name}")

def commit_and_push_changes(branch_name, commit_message):
    subprocess.run(["git", "checkout", branch_name], check=True)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
    log_message(f"[GitHub] Pushed changes to {branch_name}")

# AI Agents
shared_tools = [WebSearchTool(), ComputerTool()]

project_manager = Agent(
    name="Project Manager",
    instructions="Manage AI project development, review code, and approve PRs.",
    model="o3-mini",
    tools=shared_tools
)

backend_agent = Agent(
    name="Backend Developer",
    instructions="Develop a FastAPI backend, create endpoints, and database models.",
    model="o3-mini",
    tools=shared_tools
)

desktop_agent = Agent(
    name="Desktop App Developer",
    instructions="Develop a PyQt/Electron desktop app and ensure API integration.",
    model="gpt-4-turbo-2024-04-09",
    tools=shared_tools
)

web_agent = Agent(
    name="Web App Developer",
    instructions="Develop a React or Next.js web app and connect to the backend.",
    model="gpt-4-turbo-2024-04-09",
    tools=shared_tools
)

# Function to run tests
def run_tests():
    log_message("[+] Running tests...")

    backend_test_results = Runner.run_sync(backend_agent, "Run backend tests.")
    save_to_project("backend/test_results.log", backend_test_results.final_output)

    if "FAILED" in backend_test_results.final_output:
        log_message("[-] Tests failed. AI will request fixes.")
        return False
    return True

# AI-powered Project Execution
def main():
    log_message("[+] AI Development System Initializing...")

    # Project Manager assigns tasks
    log_message("[+] Project Manager assigning tasks...")
    Runner.run_sync(project_manager, "Start development. Assign tasks.")

    # Backend Development
    log_message("[+] Backend Agent developing backend...")
    backend_code = Runner.run_sync(backend_agent, "Generate FastAPI backend code.")
    save_to_project("backend/main.py", backend_code.final_output)

    # Web Development
    log_message("[+] Web Agent developing web app...")
    web_code = Runner.run_sync(web_agent, "Generate React/Next.js frontend.")
    save_to_project("web_app/index.js", web_code.final_output)

    # Run Tests
    if run_tests():
        branch_name = "ai-update-" + str(os.getpid())
        create_github_branch(branch_name)
        commit_and_push_changes(branch_name, "AI-generated update")
        log_message("[GitHub] AI changes committed.")

    log_message("[+] AI Development Complete! 🚀")

if __name__ == "__main__":
    main()
    root.mainloop()
