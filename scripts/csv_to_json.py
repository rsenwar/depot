"""
Csv to json converter to load data in test database.
"""
import sys
import csv
import json
import copy
import random

BOOLEAN_FIELDS = {
    'paymentdetails': {'bookingflag'}
}
INTEGER_FIELDS = {
    'paymentdetails': {'bstatus'}
    
}
FLOAT_FIELDS = {
    'paymentdetails': {'travelamount'}
}
FOREIGNKEY_FIELDS = {

}

MODEL_NAME = {
    'paymentdetails': 'goibibo.paymentdetails'
    
}
new_dict = {
    'fields': {},
    'model': 'abcd',
    'pk': 0
}
bus_ids = [1, 2, 3, 4]
email_id = 'hare.pathak@go-mmt.com'
mobile = '9971996579'
guid = 'hare.pathak@go-mmt.com'
payment_detail_csv = '/home/hareram/Downloads/paymennt_detail.csv'

BOOKINGID_ID_MAP = {}
OLD_ID_BOOKINGID_MAP = {}
guid_list = ['hare', 'hare.pathak@go-mmt.com']


def read_csv_file(src_file):
    with open(src_file, 'r') as src:
        reader = csv.DictReader(src)
        data_rows = []
        for row in reader:
            data_rows.append(row)
    return data_rows


def write_json_file(dest_file, data_list):
    with open(dest_file, 'w') as dest:
        j_data = json.dumps(data_list, indent=2)
        dest.write(j_data)


def process_raw_csv_data(data_rows, model_name):
    data_list = []
    int_fields = INTEGER_FIELDS.get(model_name, set())
    bool_fields = BOOLEAN_FIELDS.get(model_name, set())
    float_fields = FLOAT_FIELDS.get(model_name, set())
    foreign_fields = FOREIGNKEY_FIELDS.get(model_name, set())
    for row in data_rows:
        row = dict(row.items())
        for key in row:
            if key in int_fields:
                row[key] = convert_to_int(row[key])
            elif key in float_fields:
                row[key] = convert_to_float(row[key])
            elif key in bool_fields:
                row[key] = convert_to_boolean(row[key])

            if key in foreign_fields:
                row[key[:-3]] = row.pop(key)
        data_list.append(row)
    return data_list


def manipulate_sample_data(data_list, model_name):
    data_list_new = []
    for i, row in enumerate(data_list):
        d11 = copy.deepcopy(new_dict)

        d11['pk'] = i + 1
        print(model_name, MODEL_NAME.get(model_name))
        d11['model'] = MODEL_NAME.get(model_name)
        # remove id field
        id = row.pop('id', None)

        if model_name == 'paymentdetail':
            OLD_ID_BOOKINGID_MAP[id] = row['bookingid']
            BOOKINGID_ID_MAP[row['bookingid']] = i + 1
            row['id'] = random.choice(bus_ids)
            row['email'] = email_id
            row['mobile'] = mobile
            row['guid'] = random.choice(guid_list)
            if not row['payment_date']:
                row['payment_date'] = None
        d11['fields'] = row
        data_list_new.append(d11)

    return data_list_new


def convert_to_int(num):
    try:
        if num is '':
            val = None
        else:
            val = int(num)
    except Exception as ex:
        print("%s\t%s" % (num, ex))
        val = num
    return val


def convert_to_float(num):
    try:
        if num is '':
            val = None
        else:
            val = float(num)
    except Exception as ex:
        print("%s\t%s" % (num, ex))
        val = num
    return val


def convert_to_boolean(num):
    try:
        if num is '':
            val = None
        else:
            val = bool(int(num))
    except Exception as ex:
        print("%s\t%s" % (num, ex))
        val = num
    return val


def convert_file(src_file, dest_file, model_name, write_data=True):
    # read file
    data = read_csv_file(src_file)
    # process_data
    processed_data = process_raw_csv_data(data, model_name)
    manipulated_data = manipulate_sample_data(processed_data, model_name)
    if write_data:
        # write data into file
        write_json_file(dest_file, manipulated_data)
        manipulated_data = []
    return manipulated_data


if __name__ == "__main__":

    if len(sys.argv) == 2 and sys.argv[1] == 'all':
        pass
    elif len(sys.argv) < 2:
        raise Exception("Destination and source file names are not provided.")
    elif len(sys.argv) < 3:
        raise Exception("Destination file name is not provided.")
    elif len(sys.argv) < 4:
        raise Exception("model name is not provided.")

    if len(sys.argv) == 4:
        src_file = sys.argv[1]
        dest_file = sys.argv[2]
        model_name = sys.argv[3]
        convert_file(src_file, dest_file, model_name)
    else:
        data1 = convert_file(booking_detail_csv, booking_detail_json, 'paymentdetail',
                             write_data=False)
        data = data1 
        write_json_file(mixed_json, data)
