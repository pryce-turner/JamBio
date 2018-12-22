import os

"""
Directory tree:
Storage
    WO-000TEST
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
PROJECT_STORAGE = os.path.abspath(os.path.join(ENV_PATH, '../data_services/Project_Storage/'))

FASTQC_PROG = os.path.abspath(os.path.join(ENV_PATH, '../data_services/FastQC/fastqc'))

