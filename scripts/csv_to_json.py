import csv
import json


def find_string_indices(substring, text):
    # Case-insensitive search for the substring in the text
    index = text.lower().find(substring.lower())

    if index != -1:
        # If the substring is found, return start and end indices
        start_index = index
        end_index = start_index + len(substring)
        return start_index, end_index
    else:
        # If the substring is not found, return None
        return None, None


def csv_to_json(csv_file_path, json_file_path):
    result_array = []

    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")

        header = next(csv_reader)  # Assuming the first row is the header

        for row in csv_reader:
            try:
                raw_ing = row[0].strip()

                qty = row[2].strip()

                uom = row[3].strip()

                name = row[1].strip()
                name_start, name_stop = find_string_indices(name, raw_ing)

                row_array = [raw_ing]

                index_array = []

                if (
                    name != None
                    and name != ""
                    and name_start != "-"
                    and name_stop != "-"
                ):
                    index_array.append([int(name_start), int(name_stop), "INGREDIENT"])

                    if qty != None and qty != "" and qty != "-":
                        qty_start, qty_end = find_string_indices(qty, raw_ing)
                        index_array.append([int(qty_start), int(qty_end), "QUANTITY"])

                    if uom != None and uom != "" and uom != "-":
                        uom_start, uom_end = find_string_indices(uom, raw_ing)
                        index_array.append([int(uom_start), int(uom_end), "UNIT"])

                    row_array.append(index_array)
                    result_array.append(row_array)
            except:
                print("failed to parse {}".format(raw_ing))

    # Writing the JSON array to a file
    with open(json_file_path, "w") as json_file:
        json.dump(result_array, json_file, indent=2)


# Example usage
csv_file_path = "Answer 4.csv"
json_file_path = "ing_new.json"
csv_to_json(csv_file_path, json_file_path)
