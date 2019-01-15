""" Variables related to column names and sizes of worksheets
in the submission form """

general_sheet_width = 40
general_sheet_length = 40

max_sheet_width = 14
max_sheet_length = 152

# Variables for storing column names in submission sheet
STR_SAMPLE_TYPE     = 'Sample Type:'
STR_PROJECT_ID      = 'Project ID:'
STR_TUBE_ID         = 'Tube ID'
STR_POOL_NAMES      = 'Pool Names' # Pools in 'Pool Information' table
STR_POOL_ID         = 'Pool Name'  # Pools in 'Indexing Information' table
STR_LIBRARY_ID      = 'Individual Library ID'
STR_VOLUME          = 'Volume (ul)'
STR_CONCENTRATION   = 'Concentration (ng/ul)'
STR_QUANTITATION    = 'Quantitation Method'
STR_AMOUNT          = 'Total Amount (ug)'
STR_BUFFER          = 'Buffer (TE or Water)'
STR_ORGANISM        = 'Organism'
STR_I7_INDEX_NAME   = 'i7 Index Name'
STR_I7_INDEX_SEQ    = 'i7 Index Sequence'
STR_I5_INDEX_NAME   = 'i5 Index Name'
STR_I5_INDEX_SEQ    = 'i5 Index Sequence'

# These are the top left cells of the data tables.
# They serve as anchors for the loops that extract the data and populate
# the database.
INDIV_ANCHOR = STR_TUBE_ID
POOL_ANCHOR = STR_TUBE_ID
INDEX_ANCHOR = STR_POOL_ID

column_headers = [
    STR_SAMPLE_TYPE,
    STR_PROJECT_ID,
    STR_TUBE_ID,
    STR_POOL_NAMES,
    STR_POOL_ID,
    STR_LIBRARY_ID,
    STR_VOLUME,
    STR_CONCENTRATION,
    STR_QUANTITATION,
    STR_AMOUNT,
    STR_BUFFER,
    STR_ORGANISM,
    STR_I7_INDEX_NAME,
    STR_I7_INDEX_SEQ,
    STR_I5_INDEX_NAME,
    STR_I5_INDEX_SEQ
    ]
