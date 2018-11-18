# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
import sys

sys.path.append("../")



class ExtractData(object) :
    
    def __init__(self, termname, termtype, level=1):
        
        self.term_name = termname
        self.term_type = termtype
        self.level = level
        self.simu = 0.0
        self.term_value = []
        self.full_term = False
    
    def set_full(self):
        self.full_term = True
        
                    
    # add extraction value     
    def add_value(self, value, simu) :
        found = False
        for elem in self.term_value :
            if value == elem[0] :
                found = True
                break
        
        if (found == False) :
            if simu == 1 or self.simu != 1 :
            #if simu == 1 or simu > self.simu :
                self.term_value.append([value, simu])
                self.simu = simu
   
    # add extraction value     
    def remove_term_elements(self) :
        nb = len(self.term_value)
        if (nb > 0) :
            for n in range(0, nb) :
                val = self.term_value[nb - n -1]
                if val[1] != 1 :
                    self.term_value.remove(val)
    
           
    def add_term_element(self, value, simu) :
        self.remove_term_elements()
        
        added = False
        for val in self.term_value :
            if value in val:
                added= True;
                break
            elif val[0] in value :
                self.term_value.remove(val)
                break
                
        if not added :
            self.term_value.append([value, simu])
       



   