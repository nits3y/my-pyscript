from pyscript import when, document
import asyncio
import pyodide.http

# Keeps track of the current "waiting" timer so we can cancel/restart it
pending_task = None

API_URL = "https://jsonplaceholder.typicode.com/users/"


@when("keydown", "#user-id-input")
def filter_keys(event):
    """Only allow digits and Backspace. Restart the pause timer on every key."""
    allowed_control_keys = ("Backspace", "Delete", "ArrowLeft", "ArrowRight", "Tab")

    if not (event.key.isdigit() or event.key in allowed_control_keys):
        event.preventDefault()
        return

    restart_timer()


def restart_timer():
    """Cancel the old 1-second timer (if any) and start a new one."""
    global pending_task

    if pending_task is not None:
        pending_task.cancel()

    pending_task = asyncio.ensure_future(wait_and_fetch())


async def wait_and_fetch():
    """Wait 1 second of no typing, then fetch the user."""
    await asyncio.sleep(1)

    user_id = document.querySelector("#user-id-input").value

    if not user_id:
        return

    await fetch_user(user_id)


async def fetch_user(user_id):
    """Fetch user data from the API and display it (non-blocking)."""
    output = document.querySelector("#output")
    output.innerText = "Loading..."

    try:
        response = await pyodide.http.pyfetch(API_URL + user_id)

        if response.status == 200:
            data = await response.json()
            name = data["name"]
            email = data["email"]
            output.innerText = f"Found: {name} ({email})"
        else:
            output.innerText = "No user found with that ID."

    except Exception:
        output.innerText = "Error fetching user."