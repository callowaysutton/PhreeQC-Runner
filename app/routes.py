from app import app, config
from app.simulation_management import run_simulation, check_status, remove_simulation
from app.workspace_management import download_workspace, edit_file, upload_file, create_workspace, delete_workspace, get_workspaces, get_file, get_files
from app.queue_management import list_queue

# Get the URL prefix for the API
# This is set in the .env file
url_prefix = config['prefix']

# Routes for running and checking the status of simulations
app.include_router(run_simulation.router, prefix=url_prefix)
app.include_router(check_status.router, prefix=url_prefix)
app.include_router(remove_simulation.router, prefix=url_prefix)

# Routes for managing workspaces
app.include_router(download_workspace.router, prefix=url_prefix)
app.include_router(edit_file.router, prefix=url_prefix)
app.include_router(upload_file.router, prefix=url_prefix)
app.include_router(create_workspace.router, prefix=url_prefix)
app.include_router(delete_workspace.router, prefix=url_prefix)
app.include_router(get_workspaces.router, prefix=url_prefix)
app.include_router(get_file.router, prefix=url_prefix)
app.include_router(get_files.router, prefix=url_prefix)

# Route for listing the queue
app.include_router(list_queue.router, prefix=url_prefix)