import shlex
import subprocess
from pathlib import Path

import modal
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "streamlit~=1.35.0", "numpy~=1.26.4", "pandas~=2.2.2", "openai", "anthropic"
)

app = modal.App(name="example-modal-streamlit", image=image)
streamlit_script_local_path = Path(__file__).parent / "app.py"
streamlit_script_remote_path = Path("/root/app.py")

@app.function(
    image=image,
    # volumes={VOLUME_DIR: volume},
    # retries=2,
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

if not streamlit_script_local_path.exists():
    raise RuntimeError(
        "app.py not found! Place the script with your streamlit app in the same directory."
    )

streamlit_script_mount = modal.Mount.from_local_file(
    streamlit_script_local_path,
    streamlit_script_remote_path,
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
    subprocess.Popen(cmthropicl=True)

