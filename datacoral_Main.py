import json
from collections import OrderedDict

'''
primary function for flattening
takes in json_file_name and a string of top current name of object
checks whether each key value combo is nested or not
if not simply places it in a holder object to then be printed out with all combos on same level
otherwise passes to recursive step recursive_flatten
assumption is that id is a standard field in json object
this could be parameterized for a different consistency, would also then need
changing in the subsequent combine function
'''
def flatten(j, name):
    j = open_json(j)
    out_arr, list_arr, name_arr = [], [], []
    for o in j:
        id, tmp= {"id":o["id"]}, {}

        for val in o:
            if not (isinstance(o[val], dict) or isinstance(o[val], list)):
                tmp.update({val:o[val]})
            else:
                non_flat_object_flatten(val, o, name, id, list_arr, name_arr)

        out_arr.append(tmp)

    #determines if there are objects that need to be flattened on this level
    if len(name_arr) > 0: recursive_flatten(name_arr, list_arr, id)
    write_json(out_arr, name)

'''
function that passes objects back to be further flattened
if singular value can just be passed on its on with id added
otherwise needs to be indexed and id
'''
def recursive_flatten(name_arr, list_arr, id):
    __index = 0
    if len(name_arr) > 1:
        while __index < len(list_arr) and name_arr[0] == name_arr[__index]:
            list_arr[__index] = index_and_id(id, __index, list_arr[__index])
            __index+=1
        flatten(list_arr, name_arr[0])
    else:
        t = {}
        t.update(id)
        t.update(list_arr[0])
        list_arr[__index] = t
        flatten(list_arr, name_arr[0])

'''
helper function for taking key value pairs that are not simple strings
if nested they will be recursively flattened
otherwise appends entire object to holder arrays
'''
def non_flat_object_flatten(val, object, name, id, list_arr, name_arr):
    if isinstance(object[val], list):
        object[val] = list_flatten_and_id(object[val], id)
        flatten(object[val], name_helper(name)+"_"+val)
    else:
        list_arr.append(object[val])
        name_arr.append(name_helper(name)+"_"+val)

'''
determines whether object needs indexing or not
if multiple length list then does
otherise just appends id
'''
def list_flatten_and_id(object_value, id):
    if len(object_value) > 1:
        index = 0
        repl = []
        for element in object_value:
            repl.append(index_and_id(id, index, element))
            index +=1
        object_value = repl
    else:
        object_value[0].update(id)
    return object_value

'''
appends s to pluralize strings
'''
def name_helper(string):
    if string[-1].lower() == "s" and string[-2:].lower() != "ss":
        return string[:-1]
    else:
        return string

'''
adds id and index value to list objects
'''
def index_and_id(id, __index, list_val):
    t = {}
    t.update(id)
    t.update({"__index":str(__index)})
    t.update(list_val)
    return t

'''
simple json writer function
takes file name and json
outputs file as name.json
'''
def write_json(j,name):
    with open(name_helper(name) + ".json", 'w') as outfile:
        json.dump(j, outfile)
    outfile.close()

'''open_json
takes in filename or json object
assumption filename has .json format or at least 5 char long to throw exception
#if is a list of dict object already do nothing
'''
def open_json(f):

    if not (isinstance(f, dict) or isinstance(f, list)):
        try:
            with open(f) as json_file:
                mylist = list(json_file)
                #this step is done to alter the ‘asdjasd’ to be readable
                list_str = mylist[0].replace("‘","\"").replace('’','\"')
                output_json = json.loads(list_str)
            #assumption is that there is only one list per JSON
            if isinstance(output_json, dict):
                return output_json[f[:-5]]
            else:
                return output_json
        except FileNotFoundError:
            print("File not found! Try again!")
            main()
            raise
    else:
        return f

'''combiner function that will take in a file name, request all additionl files
then print out either to terminal or to a requested file
assumption is that __index and id are standard in these files as well
'''
def combine(filename):
    top = open_json(filename)
    output_list = {}
    output_list[name_adder(filename[:-5])] = top
    files = files_to_be_combined_extractor()

    for file in files:
        tmp = open_json(file)

        if len(tmp) > 1:
            for each in tmp:
                each.pop("id", None)
                index = int(each.pop("__index", None))
                directory_array = working_section_finder(file)
                working = find_working_directory(directory_array, 2, output_list)
                directory_array = directory_array[1:]

                #so far this handles double multi-nesting, not sure about deeper
                #this step checks if the current directory requires further handling
                # if so input corresponding indexed object
                if isinstance(working, list) and len(directory_array) > 1:
                    working = working[0][name_adder(directory_array[0])]
                    working[index][directory_array[-1]] = each
                #otherwise insert whole object
                else:
                    working[0][name_adder(directory_array[-1])] = tmp

        else:
            directory_array = working_section_finder(file)
            working = find_working_directory(directory_array, 1, output_list)

            tmp[0].pop("id", None)
            #length 0 so just returns element as dict
            working[0][name_adder(directory_array[-1])] = tmp[0]

    combine_print_out(output_list)

'''
function that requests user for json files to combine
'''
def files_to_be_combined_extractor():
    num_files = input("How many other files need to be combined? : ")
    file_array = []
    print("In order of least to most nested please (include full filename)")
    for n in range(1, int(num_files) + 1):
        file_array.append(input("file " + str(n) + ": "))
    return file_array


'''
printer function for combine step to offer option of outputting to terminal or file
'''
def combine_print_out(output_list):
    option = input("Would you like terminal print out (t) or local (l)? : ")
    if option.lower() == "t":
        print (json.dumps(output_list, indent=4, sort_keys=True))
    elif option.lower() == "l":
        output_name = input("Please enter desired file name (without .json), keep in mind if the file already exists it will overwrite it: ")
        write_json(output_list, output_name)
    else:
        print("Bad input, try again! :)")
        combine_print_out(output_list)


'''
function to loop through objects to find appropriate location for insertion
'''
def find_working_directory(directory_array, num, output_list):
    working = output_list[name_adder(directory_array[0])]
    directory_array = directory_array[1:]
    while len(directory_array) > num:
        working = working[name_adder(directory_array[0])]
        del directory_array[0]
    return working

'''
simple name function to add on pluralization
'''
def name_adder(name):
    if name[-1].lower() != "s":
        return name + "s"
    else:
        return name

'''
takes file names and removes .json, splitting up by '_' to return nesting array
'''
def working_section_finder(name):
    if name.find("_") == -1:
        return [name[:-5]]
    else:
        name = name[:-5]
        return name.split("_")

def main():
    if input("Would you like to flatten a JSON, Y/N? : ").lower() == "y":
        filename = input("please enter the file name: ")
        flatten(filename,name_helper(filename[:-5]))
    if input("Would you like to combine several nested files into a JSON, Y/N? : ").lower() == "y":
        filename = input("please enter the top-level object file name: ")
        combine(filename)
    print("Thank you!")

if __name__ == "__main__":
    main()
