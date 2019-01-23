import os

"""
Directory tree:

Project_Storage
    WO-000TEST
        Sample_Sheet
        FastQ_Files
        QC_Output: 2018-10-08-16-05-10
            FastQC
            MultiQC
        QC_Output: 2018-10-08-16-05-10
            FastQC
            MultiQC
"""

ENV_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_STORAGE = os.path.abspath(os.path.join(ENV_PATH, '../JamBio/Project_Storage/'))
