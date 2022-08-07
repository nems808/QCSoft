import io
import os
import tempfile
import unittest

from main import load_station_data, assemble_ts_text, save_ts_files

dirname = os.path.dirname(__file__)
input_filename = os.path.join(dirname, 'test_data/monp/ssaba1810.dat')
# The ground truth output file. Produced by an earlier, better tested software version (0.6)
# Todo: Ask Fee to produce a ts, hourly, and daily file for an arbitrary station (without cleaning it) and use that output file as the ground truth
output_filename = os.path.join(dirname, 'test_data/ts_file_truth/t1231810.dat')


class TestDatFileSave(unittest.TestCase):
    input_data = None
    data_truth = None

    def setUp(self) -> None:
        self.input_data = load_station_data([input_filename])
        self.data_truth = load_station_data([output_filename])

    def tearDown(self) -> None:
        # delete all temp files here
        pass

    def test_ts_file_assembly(self):
        # 1) Load the ground truth ts file (the one you get from Fee)
        # 2) Load the monp file for the same station and month
        # 3) Save the monp file to ts (without any cleaning)
        # TODO: 4) Compare the data for each sensor. This is not necessary anymore? Because I compare the strings
        # for the two files and they are completely equal. So this is essentially an end to end test (sort of)
        # 5) Compare that formatting is exactly the same, it's all strings after all

        text_data_input = assemble_ts_text(self.input_data)
        text_data_truth = assemble_ts_text(self.data_truth)
        self.assertEqual(text_data_input[0][1], text_data_truth[0][1])

        # test ts file save
        # Compare the saved file to the ground truth file
        with tempfile.TemporaryDirectory() as tmp:
            save_ts_files(text_data_input, tmp)
            with io.open(tmp + '/' + 't1231810.dat') as tst_f:
                with io.open(output_filename) as ref_f:
                    self.assertListEqual(list(tst_f), list(ref_f))

        # Repeating all of the above but this time processing multiple months
        file1 = os.path.join(dirname, 'test_data/monp/ssaba1809.dat')
        file2 = os.path.join(dirname, 'test_data/monp/ssaba1810.dat')
        file3 = os.path.join(dirname, 'test_data/monp/ssaba1811.dat')

        truth_file1 = os.path.join(dirname, 'test_data/ts_file_truth/t1231809.dat')
        truth_file2 = os.path.join(dirname, 'test_data/ts_file_truth/t1231810.dat')
        truth_file3 = os.path.join(dirname, 'test_data/ts_file_truth/t1231811.dat')

        station_data = load_station_data([file1, file2, file3])
        station_data_truth = load_station_data([truth_file1, truth_file2, truth_file3])

        data_as_text = assemble_ts_text(station_data)
        # data_as_text_truth = assemble_ts_text(station_data_truth)

        # Compare the saved file to the ground truth file
        with tempfile.TemporaryDirectory() as tmp:
            save_ts_files(data_as_text, tmp)
            with io.open(tmp + '/' + 't1231809.dat') as tst_f1:
                with io.open(truth_file1) as ref_f:
                    self.assertListEqual(list(tst_f1), list(ref_f))
            with io.open(tmp + '/' + 't1231810.dat') as tst_f2:
                with io.open(truth_file2) as ref_f:
                    self.assertListEqual(list(tst_f2), list(ref_f))
            with io.open(tmp + '/' + 't1231811.dat') as tst_f3:
                with io.open(truth_file3) as ref_f:
                    self.assertListEqual(list(tst_f3), list(ref_f))


if __name__ == '__main__':
    unittest.main()
