class TrieNode:
  def __init__(self):
    self.children = {}
    self.is_word = ''

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, data_wo_accent_marks, data_w_accent_marks):
        """
        For each address data (with and without accent marks) with 3 parts [province,district,ward],
        a new branch with 3 Trie nodes will be created with the following structure: 
        province -> district -> ward.
        """
        current = self.root
        i = 0
        # Insert Province term -> District term -> Ward term
        for part in data_wo_accent_marks:
            if part not in current.children:
                current.children[part] = TrieNode()
            current = current.children[part]
            current.is_word = data_w_accent_marks[i]
            i += 1
            
    def search(self, data):
        """
        For each address data without accent marks, tree will search for province or district or ward
        based on how many parts passed into the functions:
        1 -> province
        2 -> district
        3 -> ward
        During searching of district or ward, if any of its descendant node is not found,
        return False as default; otherwise it will return the desire elemnt if found.
        """
        current = self.root
        result_list = []
        for part in data:
            # if part == 'namchinh':
                # print('hahaaha', current.children)
                # print('before',result_list)
            if part not in current.children:
                return False
            current = current.children[part]
            result_list.append(current.is_word)
        return result_list

    # region draf
    # def search_node1(self, findtext, node1):
    #     current = self.root
    #     current = current.children[node1]
    #     if findtext not in current.children:
    #         return False
    #     current = current.children[findtext]
    #     return current.is_word
    # endregion draft
        
    def list_children1(self):
        """
        Return list of child nodes of root node.
        """
        current = self.root
        return list(current.children.keys())
    
    def list_children2(self, node2):
        """
        Return list of child nodes of root node's child node.
        """
        current = self.root
        current = current.children[node2]
        return list(current.children.keys())
        
    def list_children3(self, node2, node3):
        """
        Return list of child nodes of child node of root node's child node.
        """
        current = self.root
        current = current.children[node2]
        current = current.children[node3]
        return list(current.children.keys())
    