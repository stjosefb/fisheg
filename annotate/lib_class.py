from fisheg import settings


import os
import json


def get_annot_classes(dataset):
    # init class
    list_classes = [
        {'id': 1, 'name': 'background', 'color': '#000000'}
    ]

    # info file
    dataset_info_file = '/'.join([settings.BASE_DATASETS_PATH, dataset, settings.FILENAME_DATASET_INFO])

    # load data
    info_content = None
    if os.path.exists(dataset_info_file):
        with open(dataset_info_file, 'r') as json_file:
            try:
                info_content = json.load(json_file)

            except Exception as e:
                #error = str(e)
                pass

    # init info_content if file not exist
    if info_content is not None:
        list_classes.extend(info_content['classes'])

    return list_classes
