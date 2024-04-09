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
        breakFlag = False
        DistrictEqualWardFlag = False  
        districtFoundFlag = False
        wardFoundFlag = False

        inputAddress = self.preprocessing(address)
        inputAddressFIRST = inputAddress
        NotFoundProvince, NotFoundDistrict = False, False

        # =============================================================================================
        # Search for province -> output: 
        # + address without province part if found or address with N characters left out if not 
        #   N is number of retry times for searching
        # + search result list: [] if not found or [province] if found
        inputAddress1, search_result = self.findProvince(inputAddress)

        # =============================================================================================
        # Search for district -> output:
        # + address with district part being left out if found
        # + search result list: [] if not found or [province, district] if found
        if self.provinceCheck != '':
            province = search_result[-1]
            inputAddress2, search_result = self.findDistrict(1, inputAddress1)
        else:
            # In case, if can't search for province, 
            # it will use each province in total to search for district 
            # with more shift times.

            # Province is missing or not correct
            NotFoundProvince = True

            province_list = self.trie.list_children1()
            for item in province_list:   
                self.provinceCheck = item
                inputAddress2, search_result = self.findDistrict(2, inputAddress)
                if self.districtCheck != '':
                    province = search_result[0]
                    district = search_result[1]
                    break
            
            # If can't search for district, erase temp province value
            if self.districtCheck == '':
                self.provinceCheck = ''

        # =============================================================================================
        # Search for ward -> output:
        # + search result list: [] if not found or [province, district, ward] if found.
        #   Therefore, value of ward if found will always be the last value of the list [-1].
        #   In case, if district was not found before that, 
        #   [1] and [2] will be used to retrieve district and ward, respectively.
        if self.provinceCheck == '' and self.districtCheck == '':
            # -> For cases where the province and district cannot be searched beforehand,
            # ward will be searched within each district of every province, based on left half of an address.
            # -> If found, then check if there are ',,' or ', ,' in the full address, 
            # indicating that the district does not exist in the address;
            # otherwise, the province does not exist in the address.
            NotFoundDistrict = True
            province_list = self.trie.list_children1()
            quotient, remainder = divmod(len(inputAddress), 2)
            res_first = inputAddress[:quotient + remainder]
            for item in province_list:
                self.provinceCheck = item
                district_list = self.trie.list_children2(self.provinceCheck)
                for item1 in district_list:
                    self.districtCheck = item1
                    inputAddress3, search_result = self.findWard(3, res_first)
                    if self.wardCheck != '':                      
                        if address.find(',,') != -1 or address.find(', ,') != -1:
                            province = search_result[0]
                            district = ''
                        else:
                            province = ''
                            district = search_result[1]
                        ward = search_result[2]
                        breakFlag = True
                        break
                if breakFlag == True:
                    break
        elif self.districtCheck != '':
            district = search_result[-1]
            inputAddress3, search_result = self.findWard(1, inputAddress2)
            if self.wardCheck != '':
                ward = search_result[-1]	
            else:
                #thử tìm tất cả xã trong chuỗi còn lại inputAddress2
                #tìm tất cả xã trong huyện đã tìm dc: 
                ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                lengthWarlist = len(ward_list_x) - 1
                listItems = ward_list_x
                listItems2 = ward_list_x
                countItems = 0
                conditionBreak = 0
                while conditionBreak < lengthWarlist-1:
                    for item in listItems:
                        if len(item) < 3:
                            conditionBreak += 1
                            break
                        if inputAddress2.find(item) == -1: 
                            item = item[0:len(item)-1]
                        else:
                            ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                            trieData = [self.provinceCheck,self.districtCheck,ward_list_x[countItems]]
                            search_result = self.trie.search(trieData)
                            if search_result != False:
                                self.wardCheck = item
                                ward = search_result[2]
                                wardFoundFlag = True
                                break 
                        listItems2[countItems] = item
                        countItems += 1
                    listItems = listItems2
                    countItems = 0
                    if wardFoundFlag == True: 
                        break #break while
                    
                if  wardFoundFlag == False:       
                    #tìm xã bằng chuỗi trước khi tìm huyện
                    inputAddress3, search_result = self.findWard(1, inputAddress1)              
                    if self.wardCheck != '':
                        ward = search_result[-1]  #lúc này huyện và xã cùng tên
                        DistrictEqualWardFlag = True
        else:
            NotFoundDistrict = True
            district_list = self.trie.list_children2(self.provinceCheck)
            for item in district_list:
                self.districtCheck = item
                inputAddress3, search_result = self.findWard(2, inputAddress1)
                if self.wardCheck != '':
                    district = search_result[1]
                    ward = search_result[2]
                    break  

        if NotFoundDistrict == True and NotFoundProvince == True:
            pass
        elif NotFoundProvince == True and NotFoundDistrict == False:
            temp = len(inputAddressFIRST) - (inputAddressFIRST.find(self.districtCheck) + len(self.districtCheck))
            if temp < 4:
               province = ''
        elif NotFoundProvince == False and NotFoundDistrict == True:
            temp = inputAddressFIRST.find(self.provinceCheck) - (inputAddressFIRST.find(self.wardCheck) + len(self.wardCheck))
            if temp < 4:
                district = ''
        if province == 'Hà Giang' and inputAddressFIRST.find('nongtruongvietlam') != -1: #case đặc biệt, tên quá dài nên hard code =))
            ward = 'Nông Trường Việt Lâm'           
        if DistrictEqualWardFlag == True:           # xã và huyện cùng tên, nếu có kí tự ,, or , , trong address thì tức huyện missing, xoá huyện đi           
            if address.find(',,') != -1 or address.find(', ,') != -1:
                district = ''   #xoá huyện
            else:
                ward = ''   #xoá xã
        
        result = {
            "province": province,
            "district": district,
            "ward": ward
        }
        return result

    def preprocessing(self, text):
        """Remove redundant characters, lowercase text, and remove accent marks."""
        text = text.replace('\n','').lower()
        text = text.replace(',tph ','').replace('t.phố','').replace('t.phô','').replace(',t.pho','').replace(' tph ','')
        text = text.replace('tph.','').replace('tp.','').replace(',tp ','').replace(' tp ','').replace('thành phố','').replace('tỉnh','').replace(' t ','').replace(',t ','')
        text = unidecode.unidecode(text)
        text = text.replace('j','')
        #text = text.replace('z','')
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
            retry_count = 18
        elif case == 2:
            retry_count = 33

        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 18:
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                data.append(self.provinceCheck)

                if inputAddress[char_pos].isnumeric() != True:  #check kí tự khác số ?
                    data.append(inputAddress[char_pos:len(inputAddress)])
                else:
                    if inputAddress[char_pos-1].isnumeric() == True:
                        char_pos -= 1
                        data.append(inputAddress[char_pos:len(inputAddress)]) #tìm 2 số liên tiếp nếu có 
                    else:
                        data.append(inputAddress[char_pos:len(inputAddress)])  #ko có thì tìm bth

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
            retry_count = 19
        elif case == 2:
            retry_count = 49
        elif case == 3:
            retry_count = len(inputAddress)
        
        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 19:
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                data.append(self.provinceCheck)
                data.append(self.districtCheck)

                if inputAddress[char_pos].isnumeric() != True:  #check kí tự khác số ?
                    data.append(inputAddress[char_pos:len(inputAddress)])
                else:
                    if inputAddress[char_pos-1].isnumeric() == True:
                        char_pos -= 1
                        data.append(inputAddress[char_pos:len(inputAddress)]) #tìm 2 số liên tiếp
                    else:
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
                #print(f'xoá phần tử {self.wardCheck}, input còn lại: ',inputAddress)
                return inputAddress, search_result
            else:
                inputAddress = inputAddress[0:len(inputAddress)-1]
                #print('Không tìm thấy Xã nào, xoá phần tử cuối cùng khỏi input: ', inputAddress)  
        return inputAddress, search_result
