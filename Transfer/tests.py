import os

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from .transfer_settings import *
from .forms import ImportCompareForm
from .views import SubmissionExcelParser, FastQParser, DataComparison
from .constants import PROJECT_STORAGE
from .models import TubeInformation, ComponentInformation, CoreData, ExecutionStats

sample_project_path = os.path.join(PROJECT_STORAGE, 'WO-TRANSFER')

class ImportAndCompareFormTest(TestCase):

    def test_import_form_file_field_label(self):
        form = ImportCompareForm()
        self.assertTrue(form.fields['sub_sheet'].label == 'Customer Submission Sheet' or form.fields['sub_sheet'].label == None)
        self.assertTrue(form.fields['project_directory_pulldown'].label == 'Core Data Folder' or form.fields['project_directory_pulldown'].label == None)

    def test_file_upload(self):
        test_sheet_path = os.path.join(sample_project_path, 'Sample_Sheet', ' Bio Sample Details Form - dd06,bbk12.xlsx')

        with open(test_sheet_path, 'rb') as f:
            form = ImportCompareForm(
                data={'project_directory_pulldown' : sample_project_path},
                files={'sub_sheet': SimpleUploadedFile('sheet', f.read())}
                )
            assert form.is_valid(), 'Invalid form, errors: {}'.format(form.errors)

class PoolSubmissionExcelParserTest(TestCase):

    # Values from 'Pooled Library' sheet of testing spreadsheet.
    pool_values = [
        [1,'Pool1',11,51,0.1,'Qubit1','water1','human1',1],
        [2,'Pool2',12,52,0.2,'Qubit2','water2','human2',2]
    ]

    component_values = [
        ['Pool1','SAM1','Nextera XT 1',301,351,'ALL-C','CCCCCCCC','ALL-G','GGGGGGGG','High'],
        ['Pool2','SAM2','Nextera XT 2',302,352,'ALL-A','AAAAAAA','ALL-T','TTTTTTTT','High'],
        ['Pool3','SAM3','Nextera XT 3',302,353,'ALL-T','TTTTTTT','ALL-A','AAAAAAA','High']
    ]

    def setUp(self):

        sheet_path = os.path.join(PROJECT_STORAGE, 'WO-TRANSFER', 'Sample_Sheet', 'Sample_Submission_Sheet_Pool.xlsx')
        self.parser = SubmissionExcelParser(sheet_path)
        self.parser.find_columns()
        self.parser.parse_pool_submission()

    def test_init(self):

        self.assertEqual(self.parser.submission_type, 'Pooled Libraries')
        self.assertEqual(self.parser.project_id_from_sheet, 123456)

    def test_pool_column_coords(self):

        tube_coord = (2,12)
        pools_coord = (3,12)
        volume_coord = (4,12)
        conc_coord = (5,12)
        amount_coord = (6,12)
        quant_coord = (7,12)
        buff_coord = (8,12)
        org_coord = (9,12)
        pool_coord = (2,35)
        sample_coord = (3,35)
        i7_name_coord = (7,35)
        i7_seq_coord = (8,35)
        i5_name_coord = (9,35)
        i5_seq_coord = (10,35)

        self.assertEqual(tube_coord, self.parser.header_coordinates[STR_TUBE_ID])
        self.assertEqual(pools_coord, self.parser.header_coordinates[STR_POOL_NAMES])
        self.assertEqual(volume_coord, self.parser.header_coordinates[STR_VOLUME])
        self.assertEqual(conc_coord, self.parser.header_coordinates[STR_CONCENTRATION])
        self.assertEqual(amount_coord, self.parser.header_coordinates[STR_AMOUNT])
        self.assertEqual(quant_coord, self.parser.header_coordinates[STR_QUANTITATION])
        self.assertEqual(buff_coord, self.parser.header_coordinates[STR_BUFFER])
        self.assertEqual(org_coord, self.parser.header_coordinates[STR_ORGANISM])
        self.assertEqual(pool_coord, self.parser.header_coordinates[STR_POOL_ID])
        self.assertEqual(sample_coord, self.parser.header_coordinates[STR_LIBRARY_ID])
        self.assertEqual(i7_name_coord, self.parser.header_coordinates[STR_I7_INDEX_NAME])
        self.assertEqual(i7_seq_coord, self.parser.header_coordinates[STR_I7_INDEX_SEQ])
        self.assertEqual(i5_name_coord, self.parser.header_coordinates[STR_I5_INDEX_NAME])
        self.assertEqual(i5_seq_coord, self.parser.header_coordinates[STR_I5_INDEX_SEQ])

    def test_tube_objects_created(self):

        # Number of non-example rows in the "Pooled Libraries" sheet
        expected_tube_objects = 2
        expected_component_objects = 3

        all_tube_objects = TubeInformation.objects.all().count()
        all_component_objects = ComponentInformation.objects.all().count()

        self.assertEqual(expected_tube_objects, all_tube_objects)
        self.assertEqual(expected_component_objects, all_component_objects)

    def test_correct_volume(self):

        for row in self.pool_values:
            Tube_id_object = TubeInformation.objects.get(pool_id=row[1])
            actual_volume = int(Tube_id_object.volume)
            self.assertEqual(actual_volume, row[2])

    def test_correct_concentration(self):

        for row in self.pool_values:
            Tube_id_object = TubeInformation.objects.get(pool_id=row[1])
            actual_concentration = int(Tube_id_object.concentration)
            self.assertEqual(actual_concentration, row[3])

    def test_correct_sample_id(self):

        for row in self.component_values:
            Component_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_sample_id = Component_id_object.sample_id
            self.assertEqual(actual_sample_id, row[1])

    def test_correct_i7_name(self):

        for row in self.component_values:
            Component_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i7_name = Component_id_object.i7_index_name
            self.assertEqual(actual_i7_name, row[5])

    def test_correct_i5_name(self):

        for row in self.component_values:
            Component_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i5_name = Component_id_object.i5_index_name
            self.assertEqual(actual_i5_name, row[7])

    def test_correct_i7_seq(self):

        for row in self.component_values:
            Component_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i7_seq = Component_id_object.i7_index_sequence
            self.assertEqual(actual_i7_seq, row[6])

    def test_correct_i5_seq(self):

        for row in self.component_values:
            Component_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i5_seq = Component_id_object.i5_index_sequence
            self.assertEqual(actual_i5_seq, row[8])

class IndividualSubmissionExcelParserTest(TestCase):

    # Values from 'Individual Library' sheet of testing spreadsheet.
    sheet_values = [
        [1,'SAM1','Nextera XT 1',11,1,301,351,'ALL-C','CCCCCCCC','ALL-G','GGGGGGGG','High'],
        [2,'SAM2','Nextera XT 2',12,2,302,352,'ALL-A','AAAAAAA','ALL-T','TTTTTTTT','High'],
        [3,'SAM3','Nextera XT 3',13,3,302,353,'ALL-T','TTTTTTT','ALL-A','AAAAAAA','High']
    ]

    def setUp(self):

        sheet_path = os.path.join(PROJECT_STORAGE, 'WO-TRANSFER', 'Sample_Sheet', 'Sample_Submission_Sheet_Indiv.xlsx')
        self.parser = SubmissionExcelParser(sheet_path)
        self.parser.find_columns()
        self.parser.parse_individual_library_submission()

    def test_init(self):

        self.assertEqual(self.parser.submission_type, 'Individual Libraries')
        self.assertEqual(self.parser.project_id_from_sheet, 123456)

    def test_indiv_lib_column_coords(self):

        tube_coord = (2,8)
        volume_coord = (5,8)
        conc_coord = (6,8)
        sample_coord = (3,8)
        i7_name_coord = (9,8)
        i7_seq_coord = (10,8)
        i5_name_coord = (11,8)
        i5_seq_coord = (12,8)


        self.assertEqual(tube_coord, self.parser.header_coordinates[STR_TUBE_ID])
        self.assertEqual(volume_coord, self.parser.header_coordinates[STR_VOLUME])
        self.assertEqual(conc_coord, self.parser.header_coordinates[STR_CONCENTRATION])
        self.assertEqual(sample_coord, self.parser.header_coordinates[STR_LIBRARY_ID])
        self.assertEqual(i7_name_coord, self.parser.header_coordinates[STR_I7_INDEX_NAME])
        self.assertEqual(i5_name_coord, self.parser.header_coordinates[STR_I5_INDEX_NAME])
        self.assertEqual(i7_seq_coord, self.parser.header_coordinates[STR_I7_INDEX_SEQ])
        self.assertEqual(i5_seq_coord, self.parser.header_coordinates[STR_I5_INDEX_SEQ])

    def test_tube_objects_created(self):

        # Number of non-example rows in the "Individual Libraries" sheet
        expected_tube_objects = 3
        expected_component_objects = 3

        all_tube_objects = TubeInformation.objects.all().count()
        all_component_objects = ComponentInformation.objects.all().count()

        self.assertEqual(expected_tube_objects, all_tube_objects)
        self.assertEqual(expected_component_objects, all_component_objects)

    def test_correct_sample_id(self):

        for row in self.sheet_values:
            Tube_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_sample_id = Tube_id_object.sample_id
            self.assertEqual(actual_sample_id, row[1])

    def test_correct_volume(self):

        for row in self.sheet_values:
            Tube_id_object = TubeInformation.objects.get(tube_id=row[0])
            actual_volume = int(Tube_id_object.volume)
            self.assertEqual(actual_volume, row[3])

    def test_correct_concentration(self):

        for row in self.sheet_values:
            Tube_id_object = TubeInformation.objects.get(tube_id=row[0])
            actual_concentration = int(Tube_id_object.concentration)
            self.assertEqual(actual_concentration, row[4])

    def test_correct_i7_name(self):

        for row in self.sheet_values:
            Tube_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i7_name = Tube_id_object.i7_index_name
            self.assertEqual(actual_i7_name, row[7])

    def test_correct_i5_name(self):

        for row in self.sheet_values:
            Tube_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i5_name = Tube_id_object.i5_index_name
            self.assertEqual(actual_i5_name, row[9])

    def test_correct_i7_seq(self):

        for row in self.sheet_values:
            Tube_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i7_seq = Tube_id_object.i7_index_sequence
            self.assertEqual(actual_i7_seq, row[8])

    def test_correct_i5_seq(self):

        for row in self.sheet_values:
            Tube_id_object = ComponentInformation.objects.get(sample_id=row[1])
            actual_i5_seq = Tube_id_object.i5_index_sequence
            self.assertEqual(actual_i5_seq, row[10])


class ImportFastQTest(TestCase):

    # core_values = [
    #     ['dd06', 'A3', 701, 'NCGTAGTA', 500, 'NTAGAGAG'],
    #     ['bkbk12', 'A1', 703, 'NCTCGCTA', 500, 'NTAGAGAG'],
    #     ['bkbk12', 'A2', 704, 'NGAGCTAC', 500, 'NTAGAGAG'],
    #     ['bkbk12', 'A3', 705, 'NGGAGCCT', 500, 'NTAGAGAG'],
    #     ['bkbk12', 'A4', 705, 'NGGAGCCT', 500, 'NTAGAGAG'],
    #     ['dd06', 'A4', 702, 'NCCTGAGC', 501, 'NTAGTCGA'],
    #     ['dd06', 'A2', 700, 'NGTACTAG', 501, 'NTAGTCGA'],
    # ]


    fastq_files_in_folder = 1

    single_fastq_values = [
        'dd06',
        'A2',
        'NGTACTAG',
        'NTAGTCGA',
        'L004',
        'R1'
    ]

    def setUp(self):

        single_fastq_directory = os.path.join(sample_project_path, 'Single_FastQ')
        self.importer = FastQParser(single_fastq_directory, 'WO-TRANSFER')
        self.importer.parse_fastq_files()

    def test_made_one_object_per_fastq(self):

        all_core_objects = CoreData.objects.all().count()
        self.assertEqual(all_core_objects, self.fastq_files_in_folder)

    def test_correct_pool_id(self):

        core_data_object = CoreData.objects.get(sample_id=self.single_fastq_values[1])
        actual_pool = core_data_object.pool_id
        self.assertEqual(actual_pool, self.single_fastq_values[0])

    def test_correct_sample_id(self):

        core_data_object = CoreData.objects.get(pool_id=self.single_fastq_values[0])
        actual_sample = core_data_object.sample_id
        self.assertEqual(actual_sample, self.single_fastq_values[1])

    def test_correct_read(self):

        core_data_object = CoreData.objects.get(sample_id=self.single_fastq_values[1])
        actual_read = core_data_object.read
        self.assertEqual(actual_read, self.single_fastq_values[5])

    def test_correct_i7(self):

        core_data_object = CoreData.objects.get(sample_id=self.single_fastq_values[1])
        actual_i7_seq = core_data_object.i7_index_sequence
        self.assertEqual(actual_i7_seq, self.single_fastq_values[2])

    def test_correct_i5(self):

        core_data_object = CoreData.objects.get(sample_id=self.single_fastq_values[1])
        actual_i5_seq = core_data_object.i5_index_sequence
        self.assertEqual(str(actual_i5_seq), self.single_fastq_values[3])

class CompareDataTest(TestCase):

    bad_pairs_cust = [('CCCCCCCC', 'NTAGTCGA'), ('NGTACTAG', 'TTTTTTTTT')]
    bad_pairs_core = [('GGGGGGGG', 'NTAGTCGA'), ('NGGAGCCT', 'TTTTTTTTT')]

    def setUp(self):

        sheet_path = os.path.join(sample_project_path, 'Sample_Sheet', ' Bio Sample Details Form - dd06,bbk12.xlsx')
        self.parser = SubmissionExcelParser(sheet_path)
        self.parser.find_columns()
        self.parser.parse_pool_submission()

        self.importer = FastQParser(os.path.join(sample_project_path, 'FastQ_Files'), 'WO-TRANSFER')
        self.importer.parse_fastq_files()

        self.comparer = DataComparison('WO-TRANSFER')
        self.comparer.compare_data()

    def test_match_number(self):

        expected_matches = 7
        actual_matches = self.comparer.match_num

        self.assertEqual(actual_matches, expected_matches)

    def test_bad_customer_matches(self):

        expected_bad_match_num = 2
        actual_bad_match_num = len(self.comparer.no_match_cust)

        expected_bad_matches = self.bad_pairs_cust
        actual_bad_matches = self.comparer.no_match_cust

        self.assertEqual(expected_bad_matches, actual_bad_matches)
        self.assertEqual(expected_bad_match_num, actual_bad_match_num)

    def test_bad_core_matches(self):

        expected_bad_match_num = 2
        actual_bad_match_num = len(self.comparer.no_match_core)

        expected_bad_matches = self.bad_pairs_core
        actual_bad_matches = self.comparer.no_match_core

        self.assertEqual(sorted(expected_bad_matches), sorted(actual_bad_matches))
        self.assertEqual(expected_bad_match_num, actual_bad_match_num)
