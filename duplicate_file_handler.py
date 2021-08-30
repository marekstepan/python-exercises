import argparse
from collections import Counter
import hashlib
import os
import pathlib
import pprint

parser = argparse.ArgumentParser()
parser.add_argument("directory", nargs="?")
args = parser.parse_args()
if args.directory is None:
    print("Directory is not specified")
    exit()

print("Enter file format:")
file_format = input()
print("""
Size sorting options:
1. Descending
2. Ascending""")

sorting = ''
while sorting != '1' and sorting != '2':
    sorting = input("\nEnter a sorting option:\n")
    if sorting != '1' and sorting != '2':
        print("\nWrong option")

# list files in directory
file_list = []
for root, dirs, files in os.walk(args.directory):
    for name in files:
        if file_format == '' or pathlib.PurePosixPath(name).suffix == ('.' + file_format):
            file_list.append(os.path.join(root, name))

# find duplicate sizes
file_sizes = {}
for file in file_list:
    file_sizes[file] = os.path.getsize(file)

sizes = [file_sizes.get(x) for x in file_sizes]
size_frequencies = dict(Counter(sizes))
duplicate_sizes = [key for (key, value) in size_frequencies.items() if value > 1]

# sorting by files' sizes
if sorting == '1':
    duplicate_sizes.sort(reverse=True)
else:
    duplicate_sizes.sort()

# printing and filtering files of duplicate sizes
files_sizes_filtered = {}
for size in duplicate_sizes:
    print()
    print(size, " bytes")
    for file, size_value in file_sizes.items():
        if size == size_value:
            files_sizes_filtered[file] = size
            print(file)

# find duplicates by hashes
check = ''
duplicate_files_hashes = []
while check != 'yes' and check != 'no':
    check = input("\nCheck for duplicates ?\n")
    if check != 'yes' and check != 'no':
        print("\nWrong option")
if check == 'no':
    exit()
else:
    block_size = 65536
    for size in duplicate_sizes:
        for file, size_value in files_sizes_filtered.items():
            if size == size_value:
                with open(file, 'rb') as hfile:
                    hasher = hashlib.md5()
                    buf = hfile.read(block_size)
                    while len(buf) > 0:
                        hasher.update(buf)
                        buf = hfile.read(block_size)
                    duplicate_files_hashes.append([file, size, hasher.hexdigest()])

    hashes = [x[2] for x in duplicate_files_hashes]
    hash_frequencies = dict(Counter(hashes))
    duplicate_hashes = [key for (key, value) in hash_frequencies.items() if value > 1]

    # filter files by only duplicate hashes
    duplicate_files = []
    for i in duplicate_files_hashes:
        if i[2] in duplicate_hashes:
            duplicate_files.append(i)

    # print result
    current_size = 0
    current_hash = ''
    counter = 0
    for i in duplicate_files_hashes:
        if i[1] != current_size:
            current_size = i[1]
            print()
            print(current_size, " bytes")
        if i[2] != current_hash:
            current_hash = i[2]
            print("Hash: ", current_hash)
        counter += 1
        file = i[0]
        i.append(counter)
        print(f"{counter}. {file}")


# delete duplicates
def check_input_values(input_string):
    value_list = input_string.split()
    numeric_values = []
    for i in value_list:
        try:
            numeric_values.append(int(i))
        except ValueError:
            return False
    return True


check = ''
input_check = False
files_to_delete = []
while check != 'yes' and check != 'no':
    check = input("\nDelete files ?\n")
    if check != 'yes' and check != 'no':
        print("\nWrong option")
if check == 'no':
    exit()
else:
    while input_check is False or input_sequence == '':
        input_sequence = input("\nEnter file numbers to delete\n")
        if check_input_values(input_sequence) is False or input_sequence == '':
            print("\nWrong format")
        else:
            counter = 0
            files_to_delete = input_sequence.split()
            for i in duplicate_files_hashes:
                if str(i[3]) in files_to_delete:
                    counter += i[1]
                    os.remove(i[0])
            print("\nTotal freed up space: " + str(counter) + " bytes\n")
            exit()

