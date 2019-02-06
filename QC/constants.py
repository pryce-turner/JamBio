import os

"""
Directory tree:
Storage
    QC_Test
        Samples Sheet
        FastQ_Files
        QC: 2018-10-08-16-05-10
            FastQC
            MultiQC
        QC: 2018-10-08-16-05-10
            FastQC
            MultiQC
"""

ENV_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_STORAGE = os.path.abspath(os.path.join(ENV_PATH, '../JamBio/Project_Storage/'))
