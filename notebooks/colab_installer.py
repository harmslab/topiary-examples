"""
Script to install topiary in a google colab notebook. This requires two cells
that, at a minimum, look like: 

Cell #1:

#-------------------------------------------------------------------------------
import os
os.chdir("/content/")

import urllib.request
urllib.request.urlretrieve(SCRIPT_URL,"colab_installer.py")

import colab_installer
colab_installer.install_topiary(install_raxml,install_generax)
#-------------------------------------------------------------------------------

Cell #2:
#-------------------------------------------------------------------------------
import os
os.chdir("/content/")

import topiary
import colab_installer
colab_installer.initialize_environment()
colab_installer.mount_google_drive(google_drive_directory)

import numpy as np
import pandas as pd
#-------------------------------------------------------------------------------


Note: this assumes python 3.8 (the current colab default, 2022/12/07). If colab
updates from python 3.8, change:

    1. Miniconda3-py38_4.12.0-Linux-x86_64.sh
    2. conda install --channel defaults conda python=3.8 --yes
    3. Refs to /usr/local/lib/python3.8/site-packages

"""

from tqdm.auto import tqdm
import sys
import subprocess
import time
import os
import re

try:
    import google.colab
    RUNNING_IN_COLAB = True
except ImportError:
    RUNNING_IN_COLAB = False
except Exception as e: 
    err = "Could not figure out if runnning in a colab notebook\n"
    raise Exception(err) from e

miniconda = \
"""
unset PYTHONPATH
MINICONDA_INSTALLER_SCRIPT=Miniconda3-py38_4.12.0-Linux-x86_64.sh
MINICONDA_PREFIX=/usr/local
wget https://repo.anaconda.com/miniconda/$MINICONDA_INSTALLER_SCRIPT --quiet
chmod +x $MINICONDA_INSTALLER_SCRIPT
./$MINICONDA_INSTALLER_SCRIPT -b -f -p $MINICONDA_PREFIX
conda install --channel defaults conda python=3.8 --yes
conda update --channel defaults --all --yes
"""

conda_packages = \
"""
conda config --add channels conda-forge
conda config --add channels bioconda
conda install --channel defaults numpy pandas xlrd openpyxl matplotlib "muscle>=5.0" blast --yes --strict-channel-priority
"""

pip_packages = \
"""
# Install ghostscript binary (so toyplot doesn't complain)
wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs1000/ghostscript-10.0.0-linux-x86_64.tgz
tar -zxf ghostscript-10.0.0-linux-x86_64.tgz
mv ghostscript-10.0.0-linux-x86_64/gs-1000-linux-x86_64 /usr/local/bin/gs

/usr/bin/python3 -m pip install mpi4py opentree ete3 dendropy biopython pastml toytree toyplot 
"""

raxml = \
"""
wget https://github.com/amkozlov/raxml-ng/releases/download/1.1.0/raxml-ng_v1.1.0_linux_x86_64.zip
unzip raxml-ng_v1.1.0_linux_x86_64.zip
cp raxml-ng /usr/local/bin
"""

generax = \
"""
apt-get install flex bison libgmp3-dev
rm -rf GeneRax
git clone --recursive https://github.com/BenoitMorel/GeneRax
cd GeneRax
./install.sh
cp build/bin/generax /usr/local/bin
cd ..
"""

topiary = \
"""
rm -rf topiary
git clone --branch main https://github.com/harmsm/topiary.git

cd topiary

# add --allow-run-as-root to mpirun calls
for x in `echo "./topiary/generax/_generax.py ./topiary/generax/_reconcile_bootstrap.py ./topiary/_private/mpi/mpi.py"`; do
    sed -i 's/\[\"mpirun\",/\[\"mpirun\",\"--allow-run-as-root\",/g' ${x}
done

/usr/bin/python3 -m pip install . -vv
cd ..
"""



def _run_install_cmd(bash_to_run,description):
    """
    Run an installation command.

    bash_to_run : str
        bash command as a string
    description : str
        description of what is being done
    """

    no_space = re.sub(" ","_",description)
    status_file = f"/content/software/{no_space}.installed"

    if os.path.isfile(status_file):
        print(f"{description} already installed.")
        return

    os.chdir("software")

    print(f"Installing {description}... ",end="",flush=True)
    f = open(f"{no_space}_tmp-script.sh","w")
    f.write(bash_to_run)
    f.close()

    result = subprocess.run(["bash",f"{no_space}_tmp-script.sh"],
                                                    stdout=subprocess.PIPE,
                                                    stderr=subprocess.PIPE,
                                                    text=True)
    
    if result.returncode != 0:
        print(result.stdout,flush=True)
        print(result.stderr,flush=True)
        raise RuntimeError("Installation failed!")

    
    f = open(f"{no_space}_stdout.txt","w")
    f.write(result.stdout)
    f.close()

    f = open(f"{no_space}_stderr.txt","w")
    f.write(result.stderr)
    f.close()

    os.chdir("..")

    f = open(status_file,'w')
    f.write("Installed\n")
    f.close()
    
    print("Complete.",flush=True)


def install_topiary(install_raxml,install_generax):

    if RUNNING_IN_COLAB:

        os.chdir("/content/")

        description_list = ["miniconda","conda packages","pip packages"]
                        
        cmd_list = [miniconda,conda_packages,pip_packages]

        if install_raxml:
            description_list.append("raxml-ng")
            cmd_list.append(raxml)

        if install_generax:
            description_list.append("generax")
            cmd_list.append(generax)

        description_list.append("topiary")
        cmd_list.append(topiary)

        print("Setting up environment.",flush=True)

        # Make software directory (if not already there)
        os.system("mkdir -p software")

        # Add conda path to the current python session
        to_append = "/usr/local/lib/python3.8/site-packages"
        if to_append not in sys.path:
            sys.path.append(to_append)

        # Make sure that any new python session that spools up during the installations
        # has the correct site packages. 
        os.environ["PYTHONSTARTUP"] = "/content/software/python_startup.py"
        f = open("/content/software/python_startup.py","w")
        f.write("import sys\n")
        f.write("sys.path.append('/usr/local/lib/python3.8/site-packages')\n")
        f.close()


        # Install each package
        pbar = tqdm(range(len(cmd_list)))
        for i in pbar:
            _run_install_cmd(cmd_list[i],description_list[i])

            # Update status bar
            pbar.refresh()
            time.sleep(0.5)
            
        # This sleep step makes sure things are done writing to the display before
        # reset
        time.sleep(2)
        os._exit(0)


def initialize_environment():

    if RUNNING_IN_COLAB:
        
        os.environ["PYTHONPATH"] = ""
        os.environ["PYTHONSTARTUP"] = "/content/software/python_startup.py"
        os.environ["TOPIARY_MAX_SLOTS"] = "1"

        topiary._in_notebook = "colab"

        to_append = '/usr/local/lib/python3.8/site-packages'
        if to_append not in sys.path:
            sys.path.append(to_append)

        os.chdir("/content/")

def mount_google_drive(google_drive_directory):

    # Set up google drive
    if RUNNING_IN_COLAB and google_drive_directory:

        from google.colab import drive
        drive.mount('/content/gdrive/')

        working_dir = f"/content/gdrive/MyDrive/{google_drive_directory}"
        os.system(f"mkdir -p {working_dir}")
        os.chdir(working_dir)
        
    print(f"Working directory: {os.getcwd()}")