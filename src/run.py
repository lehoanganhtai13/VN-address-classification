from address_segmentation import addressSegmentation
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
dataset_file_path = os.path.join(current_directory, '..', 'dataset', 'vn_address_dataset.txt')

class Solution:
    def __init__(self):
        # list provice, district, ward for private test, do not change for any reason
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'

    def process(self, s: str):
        dataset = open(dataset_file_path, encoding="utf8").readlines()
        segmenter = addressSegmentation(dataset)
        return segmenter.segment(s)
