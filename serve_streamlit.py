import shlex
import subprocess
from pathlib import Path

import modal
from modal import Volume
from urllib.request import urlretrieve
import os

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit~=1.35.0", "openai", "anthropic"
)

app = modal.App(name="example-modal-streamlit", image=image)

streamlit_script_local_path = Path(__file__).parent / "streamlit_app.py"
print("Current working directory:", os.getcwd())
print("File path being checked:", streamlit_script_local_path)
print("File exists:", os.path.exists(streamlit_script_local_path))
streamlit_script_remote_path = Path("/root/streamlit_app.py")

# Mount the local file to the expected remote path
streamlit_script_mount = modal.Mount.from_local_file(
    streamlit_script_local_path,
    streamlit_script_remote_path,
)

print("Files in current working directory:")
for file_name in os.listdir(os.getcwd()):
    print(file_name)


VOLUME_DIR = "/cache-vol"
volume = Volume.from_name(
    "arc-dataset", create_if_missing=True
)

@app.function(
    image=image,
    volumes={VOLUME_DIR: volume},
    retries=2,
)
def dataset_setup():
    # download dataset
    print("Downloading dataset...")
    urlretrieve(
        "https://github.com/arc-community/arc",
        "/tmp/covid-19.zip",
    )

    print("Processing dataset:")
    subprocess.run("pip3 install -e \".[dev]\"", check=True)
    subprocess.run("arc download-arc-dataset", check=True)
    subprocess.run("arc show --random-id", check=True)

print("Files in current working directory:")
for file_name in os.listdir(os.getcwd()):
    print(file_name)

if not streamlit_script_local_path.exists():
    print(streamlit_script_local_path)
    raise RuntimeError(
        "streamlit_app.py not found! Place the script with your Streamlit app in the same directory."
    )

@app.function(
    allow_concurrent_inputs=100,
    mounts=[streamlit_script_mount],
)
@modal.web_server(8000)
def run():
    dataset_setup.remote()
    target = shlex.quote(str(streamlit_script_remote_path))
    cmd = f"streamlit run {target} --server.port 8000 --server.enableCORS=false --server.enableXsrfProtection=false"
    subprocess.Popen(cmd, shell=True)



