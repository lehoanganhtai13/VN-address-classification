from trie_algorithm import Trie
import unidecode
import re

class addressSegmentation():
    def __init__(self, dataset) -> None:
        """
        Params:
        -------
        trie: any
            A trie tree used as a dictionary to serch for province, district, and ward.

        provinceCheck: str, default=''
            searched province without accent marks, which is used to search instead of
            term with accent marks.

        districtCheck: str, default=''
            searched district without accent marks, which is used to search instead of
            term with accent marks.

        wardCheck: str, default=''
            searched ward without accent marks, which is used to search instead of
            term with accent marks.
        """
        
        self.trie = self.createTrie(dataset)
        self.provinceCheck = ''
        self.districtCheck = ''
        self.wardCheck = ''

    def segment(self, address):
        self.provinceCheck = ''
        self.districtCheck = ''
        self.wardCheck = ''
        province, district, ward = '', '', ''

        inputAddress = self.preprocessing(address)

        # Search for province -> output: 
        # + address without province part if found or address with N characters left out if not 
        #   N is number of retry times for searching
        # + search result list: [] if not found or [province] if found
        inputAddress1, search_result = self.findProvince(inputAddress)

        # Search for district -> output:
        # + address with district part being left out if found
        # + search result list: [] if not found or [province, district] if found
        if self.provinceCheck != '':
            province = search_result[-1]
            # print('input', inputAddress1)
            inputAddress2, search_result = self.findDistrict(1, inputAddress1)
        else:
            # In case, if can't search for province, 
            # it will use each province in total to search for district 
            # with more shift times.
            province_list = self.trie.list_children1()
            for item in province_list:   
                self.provinceCheck = item
                inputAddress2, search_result = self.findDistrict(2, inputAddress)
                #print(provinceCheck)
                if self.districtCheck != '':
                    province = search_result[0]
                    district = search_result[1]
                    break
            
            # If can't search for district, erase temp province value
            if self.districtCheck == '':
                self.provinceCheck = ''

        # Search for ward -> output:
        # + search result list: [] if not found or [province, district, ward] if found.
        #   Therefore, value of ward if found will always be the last value of the list [-1].
        #   In case, if district was not found before that, 
        #   [1] and [2] will be used to retrieve district and ward, respectively.
        if self.provinceCheck == '' and self.districtCheck == '':
            pass
        elif self.districtCheck != '':
            district = search_result[-1]
            inputAddress3, search_result = self.findWard(1, inputAddress2)
            if self.wardCheck != '':
                ward = search_result[-1]
        else:
            district_list = self.trie.list_children2(self.provinceCheck)
            for item in district_list:
                self.districtCheck = item
                inputAddress3, search_result = self.findWard(2, inputAddress1)
                if self.wardCheck != '':
                    district = search_result[1]
                    ward = search_result[2]
                    break
        
        result = {
            "province": province,
            "district": district,
            "ward": ward
        }
        return result

    def preprocessing(self, text):
        """Remove redundant characters, lowercase text, and remove accent marks."""
        text = text.replace('\n','').lower()
        text = unidecode.unidecode(text)
        #text = text.replace('j','')
        text = text.replace('w','').replace('z','g')
        return re.sub('[^A-Za-z0-9]+', '', text) 

    def createTrie(self, dataset):
        trie = Trie()
        for address in dataset:
            parts = address.replace('\n','').split(',')
            list1 = [parts[0],parts[1],parts[2]]
            list2 = [parts[3],parts[4],parts[5]]
            trie.insert(list1, list2)
        return trie

    def findProvince(self, inputAddress):
        """
        Search for province via comparing text with length increasing one char from right to left at a time
        with maximum 'num_char_check' times, if reach max time and still not search for that province, it will
        shift right one char, and it will repeat this maximum 'retry_count' times.
        """

        search_result = []
        positionMatch = 0

        retry_count = 16
        while retry_count > 0:
            if len(inputAddress) < 2:
                    break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 15:
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                if inputAddress[char_pos].isnumeric() != True:  #bỏ qua số trong tên tỉnh 
                    data.append(inputAddress[char_pos:len(inputAddress)])
                else:
                    inputAddress = inputAddress[0:char_pos] + inputAddress[char_pos+1:len(inputAddress)]
                    data.append(inputAddress[char_pos:len(inputAddress)])
          
                search_result = self.trie.search(data)
                #print('Tìm trong Trie: ',data , search_result)
                if search_result != False:
                    positionMatch = char_pos
                    self.provinceCheck = data[0]
                    break #không có tỉnh trùng hoặc tên tỉnh nằm trong tên tỉnh khác
                num_char_check += 1
                char_pos -= 1
            if self.provinceCheck != '':    
                inputAddress = inputAddress[0:positionMatch]
                #print(f'xoá phần tử {self.provinceCheck}, input còn lại: ',inputAddress)
                return inputAddress, search_result
            else:
                inputAddress = inputAddress[0:len(inputAddress)-1]
                #print('Không tìm thấy tỉnh nào, xoá phần tử cuối cùng khỏi input: ', inputAddress)
        return inputAddress, search_result

    def findDistrict(self, case, inputAddress):
        """
        Search for district via comparing text with length increasing one char from right to left at a time
        with maximum 'num_char_check' times, if reach max time and still not search for that province, it will
        shift right one char, and it will repeat this maximum 'retry_count' times.

        Based on different input case there will be different retry_count values.
        Case 1: if province is found.
        Case 2: if province is not found, has to use each province it total list to search for district with more shift times.
        """
        positionMatch = 0
        search_result = []

        retry_count = 0
        if case == 1:
            retry_count = 16
        elif case == 2:
            retry_count = 31

        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 15:
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                data.append(self.provinceCheck)
                data.append(inputAddress[char_pos:len(inputAddress)])
                search_result = self.trie.search(data)
                #print('Tìm trong Trie: ',data , search_result)
                if search_result != False:
                    positionMatch = char_pos
                    self.districtCheck = data[1]
                    break 
                num_char_check += 1
                char_pos -= 1

            if self.districtCheck != '':    
                inputAddress = inputAddress[0:positionMatch]
                #print(f'xoá phần tử {self.districtCheck}, input còn lại: ',inputAddress)
                return inputAddress, search_result
            else:
                inputAddress = inputAddress[0:len(inputAddress)-1]
                #print('Không tìm thấy Huyện nào, xoá phần tử cuối cùng khỏi input: ', inputAddress)   
        return inputAddress, search_result

    def findWard(self, case, inputAddress):
        """
        Search for ward via comparing text with length increasing one char from right to left at a time
        with maximum 'num_char_check' times, if reach max time and still not search for that province, it will
        shift right one char, and it will repeat this maximum 'retry_count' times.

        Based on different input case there will be different retry_count values.
        Case 1: if district is found.
        Case 2: if district is not found, has to use each district it total list to search for ward with more shift times.
        There will be no search case if both province and district are not found.
        """
        positionMatch = 0
        search_result = []

        retry_count = 0
        if case == 1:
            retry_count = 16
        elif case == 2:
            retry_count = 46
        
        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 15:
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                data.append(self.provinceCheck)
                data.append(self.districtCheck)
                data.append(inputAddress[char_pos:len(inputAddress)])
                search_result = self.trie.search(data)
                # print('Tìm trong Trie: ',data , search_result)
                if search_result != False:
                    positionMatch = char_pos
                    self.wardCheck = data[2]
                    break 
                num_char_check += 1
                char_pos -= 1

            if self.wardCheck != '':    
                inputAddress = inputAddress[0:positionMatch]
                #print(f'xoá phần tử {wardCheck}, input còn lại: ',inputAddress)
                return inputAddress, search_result
            else:
                inputAddress = inputAddress[0:len(inputAddress)-1]
                #print('Không tìm thấy Xã nào, xoá phần tử cuối cùng khỏi input: ', inputAddress)  
        return inputAddress, search_result
