from trie_algorithm import Trie
import unidecode
import re

class addressSegmentation():
    def __init__(self, dataset) -> None:
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
        wardFoundFlag = False  
        districtFoundFlag = False
        
        inputAddress = self.preprocessing(address)
        inputAddressFIRST = inputAddress  
        NotFoundProvince, NotFoundDistrict = False, False 
        
        # Search for province -> output: address without province part if found 
        # or address with N characters left out if not 
        # N is number of retry times for searching
        inputAddress1, search_result = self.findProvince(inputAddress)

        # Search for district -> output: address with district part being left out if found
        if self.provinceCheck != '':
            province = search_result[-1]
            inputAddress2, search_result = self.findDistrict(1, inputAddress1)
        else:
            # In case, if can't search for province, 
            # it will use each province in total to search for district 
            # with longer text
            NotFoundProvince = True  #note that's province is missing or not correct 
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

        # Search for ward =============================================================================
        if self.provinceCheck == '' and self.districtCheck == '': #tỉnh và huyện đều trống
            
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
            
        elif self.districtCheck != '' and self.provinceCheck != '': #có tỉnh và có huyện 
            district = search_result[-1]
            inputAddress3, search_result = self.findWard(1, inputAddress2)
            if self.wardCheck != '':
                ward = search_result[-1]
            	
            if search_result == False:  
                #thử tìm tất cả xã trong chuỗi còn lại inputAddress2
                #tìm tất cả xã trong huyện đã tìm dc:               
                ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                ward_list_y = []
                for item in ward_list_x:
                    if len(item) > 5:
                        ward_list_y.append(item)
                ward_list_x = ward_list_y
                lengthWarlist = len(ward_list_x) - 1
                listItems = ward_list_x
                listItems2 = ward_list_x
                countItems = 0
                sumlength = lengthWarlist*4 + 1
                while lengthWarlist > 0 and sumlength > lengthWarlist*4:
                    sumlength = 0
                    for item in listItems:
                        sumlength += len(item)
                    if sumlength <= lengthWarlist*4:
                        break                    
                    for item in listItems:
                        if len(item) < 4:
                            pass
                        else:
                            if inputAddress2.find(item) == -1:                                 
                                item = item[1:len(item)]  # xoá từ trái qua phải
                            else:
                                ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                                ward_list_y = []
                                for item in ward_list_x:
                                    if len(item) > 5:
                                        ward_list_y.append(item)
                                ward_list_x = ward_list_y
                                trieData = [self.provinceCheck,self.districtCheck,ward_list_x[countItems]]
                                search_result = self.trie.search(trieData)
                                if search_result != False:
                                    self.wardCheck = ward_list_x[countItems]
                                    ward = search_result[2]
                                    wardFoundFlag = True
                                    break 
                        listItems2[countItems] = item
                        countItems += 1
                    listItems = listItems2
                    if sumlength == 0:
                        break
                    countItems = 0
                    if wardFoundFlag == True: 
                        break #break while
                        
                if wardFoundFlag == False: #xoá từ phải qua trái
                    ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                    ward_list_y = []
                    for item in ward_list_x:
                        if len(item) > 5:
                            ward_list_y.append(item)
                    ward_list_x = ward_list_y
                    lengthWarlist = len(ward_list_x) - 1
                    listItems = ward_list_x
                    listItems2 = ward_list_x
                    countItems = 0
                    sumlength = lengthWarlist*4 + 1
                    while lengthWarlist > 0 and sumlength > lengthWarlist*4:
                        sumlength = 0
                        for item in listItems:
                            sumlength += len(item)
                        if sumlength <= lengthWarlist*4:
                            break
                        for item in listItems:
                            if len(item) < 4:
                                pass
                            else:
                                if inputAddress2.find(item) == -1: 
                                    item = item[0:len(item)-1]    #xoá từ phải qua trái
                                else:
                                    ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                                    ward_list_y = []
                                    for item in ward_list_x:
                                        if len(item) > 5:
                                            ward_list_y.append(item)
                                    ward_list_x = ward_list_y
                                    trieData = [self.provinceCheck,self.districtCheck,ward_list_x[countItems]]
                                    search_result = self.trie.search(trieData)
                                    #print('search_result: ',search_result)
                                    if search_result != False:
                                        self.wardCheck = ward_list_x[countItems]
                                        ward = search_result[2]
                                        wardFoundFlag = True                           
                                        break 
                            listItems2[countItems] = item
                            countItems += 1
                        listItems = listItems2
                        countItems = 0
                        if wardFoundFlag == True: 
                            break #break while
              
                if  wardFoundFlag == False:     #nếu vẫn false thì khả năng xã và huyện cùng tên, trong đó huyện is missing  
                    #tìm xã bằng chuỗi trước khi tìm huyện
                    inputAddress3, search_result = self.findWard(1, inputAddress1)              
                    if self.wardCheck != '':
                        ward = search_result[-1]  #lúc này huyện và xã cùng tên
                        DistrictEqualWardFlag = True
            
        else:
            NotFoundDistrict = True # new from Hung
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
            ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
            ward_list_y = []
            for item in ward_list_x:
                if len(item) > 5:
                    ward_list_y.append(item)
            ward_list_x = ward_list_y
            lengthWarlist = len(ward_list_x) - 1
            listItems = ward_list_x
            listItems2 = ward_list_x
            countItems = 0
            sumlength = lengthWarlist*4 + 1
            while lengthWarlist > 0 and sumlength > lengthWarlist*4:
                sumlength = 0
                for item in listItems:
                    sumlength += len(item)
                if sumlength <= lengthWarlist*4:
                    break                    
                for item in listItems:
                    if len(item) < 4:
                        pass
                    else:
                        if inputAddress2.find(item) == -1: 
                            item = item[1:len(item)]  #xoá từ trái qua phải
                        else:
                            ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                            ward_list_y = []
                            for item in ward_list_x:
                                if len(item) > 5:
                                    ward_list_y.append(item)
                            ward_list_x = ward_list_y
                            trieData = [self.provinceCheck,self.districtCheck,ward_list_x[countItems]]
                            search_result = self.trie.search(trieData)
                            #print('search_result: ',search_result)
                            if search_result != False:
                                self.wardCheck = ward_list_x[countItems]
                                ward = search_result[2]
                                wardFoundFlag = True                           
                                break 
                    listItems2[countItems] = item
                    countItems += 1
                listItems = listItems2
                countItems = 0
                if wardFoundFlag == True: 
                        break #break while
            if wardFoundFlag == False: #xoá từ trái qua phải
                ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                ward_list_y = []
                for item in ward_list_x:
                    if len(item) > 5:
                        ward_list_y.append(item)
                ward_list_x = ward_list_y
                lengthWarlist = len(ward_list_x) - 1
                listItems = ward_list_x
                listItems2 = ward_list_x
                countItems = 0
                sumlength = lengthWarlist*4 + 1
                while lengthWarlist > 0 and sumlength > lengthWarlist*4:
                    sumlength = 0
                    for item in listItems:
                        sumlength += len(item)
                    if sumlength <= lengthWarlist*4:
                        break                    
                    for item in listItems:
                        if len(item) < 4:
                            pass
                        else:
                            if inputAddress2.find(item) == -1: 
                                item = item[0:len(item)-1]    #xoá từ trái qua phải
                            else:
                                ward_list_x = self.trie.list_children3(self.provinceCheck, self.districtCheck)
                                ward_list_y = []
                                for item in ward_list_x:
                                    if len(item) > 5:
                                        ward_list_y.append(item)
                                ward_list_x = ward_list_y
                                trieData = [self.provinceCheck,self.districtCheck,ward_list_x[countItems]]
                                search_result = self.trie.search(trieData)
                                #print('search_result: ',search_result)
                                if search_result != False:
                                    self.wardCheck = ward_list_x[countItems]
                                    ward = search_result[2]
                                    wardFoundFlag = True                           
                                    break 
                        listItems2[countItems] = item
                        countItems += 1
                    listItems = listItems2
                    countItems = 0
                    if wardFoundFlag == True: 
                        break #break while
            
            temp = len(inputAddressFIRST) - (inputAddressFIRST.find(self.districtCheck) + len(self.districtCheck))
            if temp < 4:
               province = ''
        elif NotFoundProvince == False and NotFoundDistrict == True:
            temp = inputAddressFIRST.find(self.provinceCheck) - (inputAddressFIRST.find(self.wardCheck) + len(self.wardCheck))
            if temp < 4:
               district = ''
        if province == 'Hà Giang' and inputAddressFIRST.find('nongtruongvietlam') != -1: #case đặc biệt, tên quá dài nên hard code =))
            ward = 'Nông Trường Việt Lâm'           
        if DistrictEqualWardFlag == True:           #xã và huyện cùng tên, nếu có kí tự ,, or , , trong address thì tức huyện missing, xoá huyện đi           
            if address.find(',,') != -1 or address.find(', ,') != -1:
                district = ''   #xoá huyện
            else:
                ward = ''   #xoá xã
            
        if district == '' and ward == '':  #chỉ có tỉnh, tìm huyện lần cuối
            #khi này có tỉnh mà ko tìm dc huyện, vậy sẽ tìm tất cả huyện trong tỉnh đó coi có xuất hiện trong input ko?
            district_list_x = self.trie.list_children2(self.provinceCheck)
            lengthWarlist = len(district_list_x) - 1
            listItems = district_list_x
            listItems2 = district_list_x
            countItems = 0
            sumlength = lengthWarlist*3 + 1
            while lengthWarlist > 0 and sumlength > lengthWarlist*3:
                sumlength = 0
                for item in listItems:
                    sumlength += len(item)
                if sumlength <= lengthWarlist*3:
                    break                    
                for item in listItems:
                    if len(item) < 3:
                        pass
                    else:
                        if inputAddress1.find(item) == -1: 
                            item = item[1:len(item)]  #xoá từ trái qua phải
                        else:
                            district_list_x = self.trie.list_children2(self.provinceCheck)
                            trieData = [self.provinceCheck,district_list_x[countItems]]
                            search_result = self.trie.search(trieData)
                            #print('search_result: ',search_result)
                            if search_result != False:
                                self.districtCheck = district_list_x[countItems]
                                district = search_result[1]
                                districtFoundFlag = True                           
                                break 
                    listItems2[countItems] = item
                    countItems += 1
                listItems = listItems2
                countItems = 0
                if districtFoundFlag == True: 
                    break #break while
                    
            if districtFoundFlag == False: #xoá từ trái qua phải
                district_list_x = self.trie.list_children2(self.provinceCheck)
                lengthWarlist = len(district_list_x) - 1
                listItems = district_list_x
                listItems2 = district_list_x
                countItems = 0
                sumlength = lengthWarlist*3 + 1
                while lengthWarlist > 0 and sumlength > lengthWarlist*3:
                    sumlength = 0
                    for item in listItems:
                        sumlength += len(item)
                    if sumlength <= lengthWarlist*3:
                        break                    
                    for item in listItems:
                        if len(item) < 3:
                            pass
                        else:
                            if inputAddress1.find(item) == -1: 
                                item = item[0:len(item)-1]    #xoá từ trái qua phải
                            else:
                                district_list_x = self.trie.list_children2(self.provinceCheck)                              
                                trieData = [self.provinceCheck,district_list_x[countItems]]
                                search_result = self.trie.search(trieData)
                                #print('search_result: ',search_result)
                                if search_result != False:
                                    self.districtCheck = district_list_x[countItems]
                                    district = search_result[1]
                                    districtFoundFlag = True                           
                                    break 
                        listItems2[countItems] = item
                        countItems += 1
                    listItems = listItems2
                    countItems = 0
                    if districtFoundFlag == True: 
                        break #break while        
        result = {
            "province": province,
            "district": district,
            "ward": ward
        }
        return result

    def preprocessing(self, text):
        """Remove redundant characters, lowercase text, and remove accent marks."""
        text = text.replace('\n','').lower()
        text = text.replace(',tph ','').replace('t.phố','').replace('t.phô','').replace(',t.pho','').replace(' tph ','').replace('tph.','').replace('tp.','').replace(',tp ','').replace(' tp ','').replace('thành phố','')
        text = text.replace('tỉnh','').replace(' t ','').replace(',t ','')  
        text = text.replace('huyện','')
        
        text = unidecode.unidecode(text)
        
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
        positionMatch = 0
        search_result = []

        retry_count = 0
        if case == 1:
            retry_count = 18 #change 16 to 18 # new from Hung
        elif case == 2:
            retry_count = 33 #change 31 to 33 # new from Hung

        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 18: #change 16 to 18 # new from Hung
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0: # new from Hung ( correct last bug)
                    break
                data = []                       
                data.append(self.provinceCheck)
                # begin new from Hung
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
        positionMatch = 0
        search_result = []

        retry_count = 0
        if case == 1:
            retry_count = 19  # new from Hung
        elif case == 2:
            retry_count = 49 # new from Hung
        elif case == 3: # new from Hung
            retry_count = len(inputAddress) # new from Hung
        while retry_count > 0:
            if len(inputAddress) < 2:
                break
            retry_count -= 1
            num_char_check = 0
            char_pos = len(inputAddress) - 1
            while num_char_check < 19: # new from Hung 19
                if len(inputAddress) < 2 or len(inputAddress) - num_char_check == 0:
                    break
                data = []
                data.append(self.provinceCheck)
                data.append(self.districtCheck)
                # start new from Hung
                if inputAddress[char_pos].isnumeric() != True:  #check kí tự khác số ?
                    data.append(inputAddress[char_pos:len(inputAddress)])
                else:
                    if inputAddress[char_pos-1].isnumeric() == True:
                        char_pos -= 1
                        data.append(inputAddress[char_pos:len(inputAddress)]) #tìm 2 số liên tiếp
                    else:
                        data.append(inputAddress[char_pos:len(inputAddress)])                
                
                search_result = self.trie.search(data)
                #print('Tìm trong Trie: ',data , search_result)
                if search_result != False:
                    positionMatch = char_pos
                    self.wardCheck = data[2]
                    break 
                num_char_check += 1
                char_pos -= 1

            if self.wardCheck != '':    
                inputAddress = inputAddress[0:positionMatch]
                #print(f'xoá phần tử {self.wardCheck }, input còn lại: ',inputAddress) #thêm self.
                return inputAddress, search_result
            else:
                inputAddress = inputAddress[0:len(inputAddress)-1]
                #print('Không tìm thấy Xã nào, xoá phần tử cuối cùng khỏi input: ', inputAddress)  
        return inputAddress, search_result
