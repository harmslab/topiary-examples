import os
import subprocess
import shutil
import sys

def run_cmd(cmd, shell=True):
    """Utility to run shell commands from within python."""
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=shell, check=True)

def setup_topiary_stack(google_drive_directory="", ncbi_api_key=""):

    # 1. Create working directory & mount drive
    google_drive_directory = google_drive_directory.strip()
    if google_drive_directory != "":
        from google.colab import drive
        drive.mount('/content/gdrive')
        working_dir = f"/content/gdrive/MyDrive/{google_drive_directory}"
        os.makedirs(working_dir, exist_ok=True)
        os.chdir(working_dir)
        
    os.makedirs("src", exist_ok=True)
    os.chdir("src")

    # 2. Setup Binary Directory
    bin_dir = "/content/bin"
    os.makedirs(bin_dir, exist_ok=True)
    if bin_dir not in os.environ['PATH']:
        os.environ['PATH'] = f"{bin_dir}:{os.environ['PATH']}"
    os.environ['BIN_DIR'] = bin_dir

    # 3. Download and install tools
    tools = {
        "ncbi-blast-2.17.0+-x64-linux.tar.gz": "https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.17.0+-x64-linux.tar.gz",
        "muscle-linux-x86.v5.3": "https://github.com/rcedgar/muscle/releases/download/v5.3/muscle-linux-x86.v5.3",
        "generax-linux-x86.v2.1.3a": "https://github.com/harmslab/GeneRax/releases/download/v2.1.3a/generax-linux-x86.v2.1.3a",
        "raxml-ng-linux-x86.v2.0.0a": "https://github.com/harmslab/raxml-ng/releases/download/v2.0.0a/raxml-ng-linux-x86.v2.0.0a"
    }

    for filename, url in tools.items():
        if not os.path.exists(filename):
            print(f"Downloading {filename}...")
            run_cmd(f"wget {url}")

    # 4. Extract and Move Binaries
    # Blast
    if os.path.exists("ncbi-blast-2.17.0+"):
        for f in os.listdir("ncbi-blast-2.17.0+/bin"):
            shutil.copy(os.path.join("ncbi-blast-2.17.0+/bin", f), bin_dir)
    else:
        run_cmd("tar -zxf ncbi-blast-2.17.0+-x64-linux.tar.gz")
        run_cmd(f"cp ncbi-blast-2.17.0+/bin/* {bin_dir}/")

    # Others
    shutil.copy("muscle-linux-x86.v5.3", os.path.join(bin_dir, "muscle"))
    shutil.copy("generax-linux-x86.v2.1.3a", os.path.join(bin_dir, "generax"))
    shutil.copy("raxml-ng-linux-x86.v2.0.0a", os.path.join(bin_dir, "raxml-ng"))

    # Make executable
    run_cmd(f"chmod 755 {bin_dir}/*")

    # 5. System dependencies and MPI
    print("Installing system dependencies...")
    run_cmd("apt-get update && apt-get install -y libopenmpi-dev openmpi-bin")
    
    os.environ.update({
        "TOPIARY_MAX_SLOTS": "2",
        "TOPIARY_MPI_OVERSUBSCRIBE": "1",
        "OMPI_ALLOW_RUN_AS_ROOT": "1",
        "OMPI_ALLOW_RUN_AS_ROOT_CONFIRM": "1"
    })
    
    print("Installing mpi4py...")
    run_cmd(f"{sys.executable} -m pip install mpi4py")

    # 6. Install Topiary
    try:
        import topiary
    except (ImportError,ModuleNotFoundError):
        # If topiary-source exists but is invalid (e.g. interrupted clone), remove it
        if os.path.exists("topiary-source"):
            if not os.path.exists(os.path.join("topiary-source","pyproject.toml")):
                print("topiary-source found but seems invalid. Removing and re-cloning...")
                shutil.rmtree("topiary-source")

        if not os.path.exists("topiary-source"):
            print("Cloning topiary source...")
            run_cmd("git clone https://github.com/harmsm/topiary topiary-source")
        
        os.chdir("topiary-source")
        print("Installing topiary...")
        run_cmd(f"{sys.executable} -m pip install .")
        print("Installing dev dependencies...")
        run_cmd(f"{sys.executable} -m pip install coverage flake8 pytest genbadge pytest-mock")
        os.chdir("..")

    # Final Config
    if ncbi_api_key.strip() != "":
        os.environ['NCBI_API_KEY'] = ncbi_api_key.strip()
    
    os.chdir("..")
    print("Setup complete.")

