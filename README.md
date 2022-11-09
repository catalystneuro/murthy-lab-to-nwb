# murthy-lab-to-nwb
NWB conversion scripts for Murthy lab data to the [Neurodata Without Borders](https://nwb-overview.readthedocs.io/) data format.

## Basic installation
You can install the latest release of the package with pip:

```
pip install murthy-lab-to-nwb
```
### Running a specific conversion

Once you have installed the package with pip, you can run any of the conversion scripts in a notebook or a python file.

You can run any of the scripts on the following list:

* [Convert one courtship session, Cowley 2022](https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_courtship_convert_session.py)
* [Convert one imaging session, Cowley 2022](https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_imaging_convert_session.py)
* [Convert all courtship sessions, Cowley 2022](https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_courtship_convert_all.py)
* [Convert all imaging sessions, Cowley 200](https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_imaging_convert_all.py)
* [Convert one session, Li 2022](https://github.com/catalystneuro/murthy-lab-to-nwb/blob/main/src/murthy_lab_to_nwb/li2022ecephys/li2022ecephys_convert_session.py)

## Installation from Github
Another option is to install the package directly from Github. This option has the advantage that the source code can be modifed if you need to amend some of the code we originally provided to adapt to future experimental differences. To install the conversion from GitHub you will need to use `git` ([installation instructions](https://github.com/git-guides/install-git)). We also recommend the installation of `conda` ([installation instructions](https://docs.conda.io/en/latest/miniconda.html)) as it contains all the required machinery in a single and simple instal

From a terminal (note that conda should install one in your system) you can do the following:

```
git clone https://github.com/catalystneuro/murthy-lab-to-nwb
cd murthy-lab-to-nwb
conda env create --file make_env.yml
conda activate murthy-lab-to-nwb-env
```

This creates a [conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/environments.html) which isolates the conversion code from your system libraries.  We recommend that you run all your conversion related tasks and analysis from the created environment in order to minimize configuration or libraries issues.

Alternatively, if you want to avoid conda altogether (for example if you use another virtual environment tool) you can install the repository with the following commands using only pip:

```
git clone https://github.com/catalystneuro/murthy-lab-to-nwb
cd murthy-lab-to-nwb
pip install -e .
```

Note:
both of the methods above install the repository in [editable mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs)



### Running a specific conversion
To run a specific conversion for a full session you can see here the following examples

```
python src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_courtship_convert_session.py
python src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_imaging_convert_session.py
python src/murthy_lab_to_nwb/li2022ecephys/li2022ecephys_convert_session.py
```

For running the full conversion of all the data the following script is available:
```
python src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_courtship_convert_all.py
```

You might need to install first some conversion specific dependencies that are located in each conversion directory:
```
pip install -r src/murthy_lab_to_nwb/cowley2022mapping/cowley2022mapping_requirements.txt
```

## Repository structure
Each conversion is organized in a directory of its own in the `src` directory:

    murthy-lab-to-nwb/
    ├── LICENSE
    ├── make_env.yml
    ├── pyproject.toml
    ├── README.md
    ├── requirements.txt
    ├── setup.py
    └── src
        ├── __init__.py
        └── murthy_lab_to_nwb
            ├── __init__.py
            ├── cowley2022mapping
            │   ├── cowley2022mapping_courtship_convert_session.py
            │   ├── cowley2022mapping_imaging_convert_session.py
            │   ├── cowley2022mapping_nwbconverter.py
            │   ├── cowley2022mapping_requirements.txt
            │   ├── __init__.py
            │   ├── interfaces
            │   ├── metadata
            │   ├── utils
            │   ├── widget_demostration_courtship.ipynb
            │   └── widget_demostration_imaging.ipynb
            └── li2022ecephys
                ├── __init__.py
                ├── li2022ecephys_convert_session.py
                ├── li2022ecephysinterface.py
                ├── li2022ecephysnwbconverter.py
                └── li2022ecephys.yaml_.py
                └── __init__.py

 For example, for the conversion `cowley2022mapping` you can find a directory located in `src/murthy-lab-to-nwb/cowley2022mapping`. Inside each conversion directory you can find the following files:

* `cowley2022mapping_courtship_convert_session.py`: this runs a nwb conversion for a courtship session.
* `cowley2022mapping_courtship_convert_all.py`: this runs the conversion for all the sessions in courtship.
* `cowley2022mapping_imaging_convert_session.py`: this runs a nwb conversion for an imaging session.
* `cowley2022mapping_requirements.txt`: dependencies specific to this conversion specifically.
* `widget_demostration_courtship.ipynb`  jupyter notebook with visulization tools for the courtship nwb file
* `widget_demostration_imaging.ipynb`  jupyter notebook with visulization tools for the imaging nwb file

Plus the following directories:
* `interfaces` directory which holds the interfaces required in this conversion.
* `metadata` directory which holds the editable yaml metadata files to add extra metadata to the conversions.
* `utils` miscellaneous utilities for the conversion.
