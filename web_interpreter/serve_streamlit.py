import shlex
import subprocess
from pathlib import Path

import modal
import os

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit~=1.35.0", "numpy~=1.26.4", "pandas~=2.2.2", "openai", "anthropic"
).apt_install(
    "git"
).run_commands(
    [
        "git clone https://github.com/arc-community/arc /root/arc",
        "cd /root/arc && pip3 install -e \".[dev]\"",
        "python3 -m venv .venv",
        ". .venv/bin/activate",
        "cd /root/arc && pip3 install -e \".[dev]\"",
        "mkdir -p /root/.arc/cache/dataset",
        "cd /root/arc && arc download-arc-dataset",
        "cd /root/arc && arc show --random-id",
    ]
)

app = modal.App(name="streamlit-sonnet-3.5-interpreter", image=image)

files = [
    "streamlit_app.py",
    "riddles_list.json",
    "vis_util.py"
]

local_paths = []
remote_paths = []
for file in files:
    local_path = Path(__file__).parent / file
    remote_path = Path("/root/") / file
    local_paths.append(local_path)
    remote_paths.append(remote_path)

mounts = []
for local_path, remote_path in zip(local_paths, remote_paths):
    mounts.append(modal.Mount.from_local_file(local_path, remote_path))

@app.function(
    allow_concurrent_inputs=100,
    mounts=mounts,
)
@modal.web_server(8000)
def run():
    target = shlex.quote(str(remote_paths[0]))
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    print("Listing all files and directories in the current directory:")
    print(os.listdir('.'))
    print("Current working directory:", os.getcwd())
    subprocess.Popen(cmd, shell=True)