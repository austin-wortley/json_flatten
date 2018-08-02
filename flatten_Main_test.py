import unittest
import io
import sys
from unittest.mock import patch
from datacoral_Main import combine_print_out, name_helper, index_and_id, list_flatten_and_id, name_adder, working_section_finder, files_to_be_combined_extractor,find_working_directory, main, open_json

class TestHelperMethods(unittest.TestCase):

    def testNameHelper(self):
        self.assertEqual("restaurant", name_helper("restaurants"))
        self.assertEqual("restaurant_address", name_helper("restaurant_address"))
        self.assertEqual("score", name_helper("scores"))

    def test_Index_and_Id(self):
        id = {"id": "1234567890"}
        index = 1
        val = {"version": "asdjasd","borough": "Bronx", "cuisine": "Bakery"}
        outval = {"id": "1234567890","__index":str(index),"version": "asdjasd","borough": "Bronx", "cuisine": "Bakery"}
        self.assertEqual(outval, index_and_id(id, index, val))

    def test_list_flatten_and_id(self):
        id = {"id": "1234567890"}
        single_val = [{"version": "asdjasd","borough": "Bronx", "cuisine": "Bakery"}]
        multi_val =[{"testkey1":"testkey1"},{"testkey2":"testkey2"},{"testkey3":"testkey3"}]
        mult_response = [{"id": "1234567890","__index": "0","testkey1":"testkey1"},{"id": "1234567890","__index": "1","testkey2":"testkey2"},{"id": "1234567890","__index": "2","testkey3":"testkey3"}]
        single_val = list_flatten_and_id(single_val, id)
        multi_val = list_flatten_and_id(multi_val, id)
        self.assertEqual(single_val, [{"id": "1234567890","version": "asdjasd","borough": "Bronx", "cuisine": "Bakery"}])
        self.assertEqual(multi_val, mult_response)


    def test_name_adder(self):
        self.assertEqual("address", name_adder("address"))
        self.assertEqual("scores", name_adder("score"))

    def test_working_section_finder(self):
        self.assertEqual(["application"], working_section_finder("application.json"))
        self.assertEqual(["application", "name", "location"], working_section_finder("application_name_location.json"))


    def test_find_working_directory(self):
        output_list = {"applications" : {"names": {"locations" : {"yayy" : "goal"}}}}
        directory_array = ["application", "name", "location"]
        self.assertEqual({"yayy" : "goal"},find_working_directory(directory_array, 0, output_list))


    def test_files_to_be_combined_extractor(self):
        user_input = ['3', "restaurant_grade.json", "restaurant_address.json", "restaurant_grade_score.json"]
        with patch('builtins.input', side_effect=user_input):
            test_arr = files_to_be_combined_extractor()
            self.assertEqual(user_input[1:], test_arr)

    def test_combine_print_out(self):
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        test_list = {"id": "58b868503c6f4d322fa8f552", "__index": "0", "x": 1, "y": 2}
        with patch('builtins.input', side_effect=["t"]):
            combine_print_out(test_list)
            sys.stdout = sys.__stdout__
        self.assertEqual('{\n    "__index": "0",\n    "id": "58b868503c6f4d322fa8f552",\n    "x": 1,\n    "y": 2\n}\n', capturedOutput.getvalue())

    def test_main(self):
        user_input_flatten = ["y", "restaurants.json", "n"]
        with patch('builtins.input', side_effect=user_input_flatten):
            main()
            restaurant_grade_score = [{"id": "58b868503c6f4d322fa8f552", "__index": "0", "x": 1, "y": 2}, {"id": "58b868503c6f4d322fa8f552", "__index": "1", "x": 11, "y": 22}]
            self.assertEqual(restaurant_grade_score, open_json('restaurant_grade_score.json'))
        user_input_combine = ["n", "y", "restaurant.json", '3', "restaurant_grade.json", "restaurant_address.json", "restaurant_grade_score.json", 'l', 'test_main']
        with patch('builtins.input', side_effect=user_input_combine):
            main()
            def json_comparison_helper(json1, json2):
                fields = ["\"restaurants\": [{", "\"id\": \"58b868503c6f4d322fa8f552\"", "\"version\": \"asdjasd\"", "\"borough\": \"Bronx\"", "\"cuisine\": \"Bakery\"",
                 "\"name\": \"Morris Park Bake Shop\"", "\"building\": \"1007\"", "\"street\": \"Morris Park Ave\"", "\"zipcode\": \"10462\"",
                 "date", "\"grade\": \"A\"", "{\"x\": 11, \"y\": 22}", "{\"x\": 1, \"y\": 2}"]
                for field in fields:
                    stringList1, stringList2 = str(json1), str(json2)
                    index1, index2 = stringList1.find(field), stringList2.find(field)
                    if  (index1 == -1 or index2 == -1) :
                        print("field : " + field + " 1 : " + str(index1) + " 2:"  + str(index2))
                        return False
                return True
            tester, test_main = open("tester.json"), open("test_main.json")
            tester_list, test_main_list = list(tester), list(test_main)
            tester.close()
            test_main.close()
            self.assertTrue(json_comparison_helper(tester_list, test_main_list))




if __name__ == '__main__':
    unittest.main()
