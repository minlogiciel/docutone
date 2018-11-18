#-*- encoding:utf-8 -*-
from __future__ import (unicode_literals)

import sys,os, re
import codecs
import math
import datetime
if False :
    import networkx as nx
import numpy as np

#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from docutone.utils import variables
    
sentence_delimiters = ['?', '？', '!', '！', ';', '；', ',', '，','.', '．', '。', '…', '\n']
word_delimiters     = [':' , '：', '、', '．'] 
simple_p = "@#$%&*_+|\'\"/￥";
double_p = "()《》“”‘’{}[]（）<>「」【】〖〗";
alpha_char = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
alpha_char1 = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ";

digital_char = "０１２３４５６７８９零一二三四五六七八九十百廿0123456789";

digital_romain = ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx'
                'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX'
                ]
allow_speech_tags = ['an', 'i', 'j', 'l', 'n', 'nr', 'nrfg', 'ns', 'nt', 'nz', 't', 'v', 'vd', 'vn', 'eng']

chinese_number = {'零':0, '十':10,'百':100, '千':1000, '万':10000, '一' : 1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7,'八':8, '九':9}
chinese_number_units = ['', '十', '百', '千', '万', '十', '百', '千']

chinese_num_char = '零一二三四五六七八九十百千万'

english_number = {0:'零', 1:'一', 2:'二', 3:'三', 4:'四', 5:'五', 6:'六', 7:'七',8:'八', 9:'九'}


# for Python 3.x and up
text_type    = str
string_types = (str,)
xrange       = range


def get_default_vocabulary_file(fname=None):
    path = os.path.join(variables.BASE_DIR, 'data/dict')
    if not os.path.exists(path) :
        os.mkdir(path)
    if fname == None :
        return os.path.join(path, 'docutone.dict')
    else :
        return os.path.join(path, fname)
    
def get_default_wordvect_file(fname=None):
    path = os.path.join(variables.BASE_DIR, 'data/dict')
    if not os.path.exists(path) :
        os.mkdir(path)
    if fname == None :
        return os.path.join(path, 'docutone.w2v')
    else :
        return os.path.join(path, fname)
        
   
def get_ner_filename() :
    root = os.path.join(variables.PYTHON_SRC, 'data/ner')
    if not os.path.exists(root) :
        os.mkdir(root)
    return os.path.join(root, 'ner.txt')


def get_defined_ner_file(filename):
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(path, 'text/'+filename)


def get_default_stop_words_file():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(path, 'text/stopwords.txt')

def get_default_suggest_words_file():
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(path, 'text/suggestwords.txt')

def write_document_table(filename, tabs) :
    filename += ".txt"
    f = codecs.open(filename, 'w', 'utf-8')
    for key, values in tabs.items() :
        f.write(("0 %s\n" % (key)))
        i = 1
        for elem in values :
            f.write(("%d %s\n" % (i, elem[0])))
            i += 1
        f.write("\n")
    f.close()
    
    
def load_document_table(filename) :
    all_keywords = {}    
    if os.path.exists(filename) :
        f = codecs.open(filename, 'r', 'utf-8')
        keywords = []
        categorie = None
        for line in f :
            line = line.strip() 
            if len(line) > 0:
                if ' ' in line :
                    nid, title = line.split(' ', 1)
                    if nid[0] == '#' :
                        continue
                    nid = int(nid) 
                    title = title.strip()
                    if nid == 0 :
                        if categorie != None :
                            all_keywords[categorie] = keywords
                        
                        # init tab
                        keywords = []
                        categorie = title
                    else :
                        keywords.append([title, nid])
                else :
                    if line[0] == '#' :
                        continue
                    keywords.append([line, 1])
        # last document type keywords
        if categorie != None :
            all_keywords[categorie] = keywords        
        f.close()
    return all_keywords

def convert_chinese_num(word):
    
    
    # english-number = [1,2,3]
    
    base1 = 1
    total = 0
    base2 = 10000
    
    nb = len(word)
    g = 0 
    for n in range(0, nb) : 
        w = word[nb-n-1]
        d =  chinese_number[w]
       
        if d == 0 :
            if g == 10 :
                total += base1
        elif d%10 == 0 :
            if n == nb -1 :
                total += d*base1
            else :
                if base1 < 10000 :
                    base1 = d
                else :
                    base1 = d * base2
                    if g == 10 and g<d :
                        total = g * base2 + total
                    
        else :
            total += d * base1
        g = d

    return total
    
def convert_english_num(N):
    
    
    base = 0
    base2 = 0
    base3 = 0
    ret = ''
    
    
    
    while N >= 1 :
        b = N%10
        N = int(N/10)
        
        if b == 0 :
            if base2 >= 1 and base3 == 0:
                base3 = 1
                ret = english_number[0] + ret
            
            if base == 4 :
                unit = chinese_number_units [base]
                ret = unit + ret
            
        else :
            g = english_number[b]

            unit = chinese_number_units [base]
            
            base2 += 1
            
            if (base == 1 or base == 5) and b == 1:
                ret = unit + ret
            else :    
                ret = g + unit + ret
        base += 1       
    return ret                   
    

def load_ners() :
 
    all_tags = {}
    
    filename  = get_ner_filename()
    if os.path.exists(filename) :
        f = codecs.open(filename, 'r', 'utf-8')
    
        for line in f :
            line = line.strip() 
            if len(line) > 0:
                if ' ' in line :
                    name, tag = line.split(' ', 1)
                    all_tags[name] = tag
                else :
                    all_tags[line] = "ORG"
        f.close()
    return all_tags


def write_ners(tables) :
    filename  = get_ner_filename()
    f = codecs.open(filename, 'w', 'utf-8')
    
    sorted_tab = sorted(tables.items(), key=lambda x: x[0])
    for elem in sorted_tab :
        f.write(("%s %s\n" % (elem[0], elem[1])))
    f.close()


def is_delimiter(ch):
    if ch in sentence_delimiters or ch in word_delimiters or ch in simple_p or ch in double_p :
        return True
    else :
        False
    


def normalize_sentence(sentence):
    """
    delete \r in sentence 
    replace \u3000 => ' '
    delete '\ufeff'
    delete '\u300A'
    delete '\u300B'
    delete '\uF06C'
    """

    string = ''
    s = sentence.split(' ')
    prev_p = ''
    for p in s :
        if len(p) > 0 :
            if len(string) and p[0] not in "年月日" :
                s1 = string[-1]
                if s1 in digital_char or s1 in sentence_delimiters or s1 in word_delimiters or s1 in alpha_char or s1 in alpha_char1:
                    string += ' '
            string += p
            if p[-1] in "章节条" :
                if len(p) > 1 :
                    if p[-2] in digital_char :
                        string += ' '
                elif len(prev_p) > 0 :
                    if prev_p[-1] in digital_char :
                        string += ' '
            prev_p = p

    s = string.replace('\u3000', ' ').replace('\ufeff', '').replace('\ue5e5', '').replace('\r', '')
    s = s.replace('\u300A', '').replace('\u300B', '').replace('\uF06C', '').strip()
 

    return s



def as_text(v):  ## 生成unicode字符串
    if v is None:
        return None
    elif isinstance(v, bytes):
        return v.decode('utf-8', errors='ignore')
    elif isinstance(v, str):
        return v
    else:
        raise ValueError('Unknown type %r' % type(v))

def is_text(v):
    return isinstance(v, text_type)



class AttrDict(dict):
    """Dict that can get attribute by dot"""
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def combine(word_list, window = 2):
    """构造在window下的单词组合，用来构造单词之间的边。
    
    Keyword arguments:
    word_list  --  list of str, 由单词组成的列表。
    windows    --  int, 窗口大小。
    """
    if window < 2: window = 2
    for x in xrange(1, window):
        if x >= len(word_list):
            break
        word_list2 = word_list[x:]
        res = zip(word_list, word_list2)
        for r in res:
            yield r

def get_similarity(word_list1, word_list2):
    """默认的用于计算两个句子相似度的函数。

    Keyword arguments:
    word_list1, word_list2  --  分别代表两个句子，都是由单词组成的列表
    """
    words   = list(set(word_list1 + word_list2))        
    vector1 = [float(word_list1.count(word)) for word in words]
    vector2 = [float(word_list2.count(word)) for word in words]
    
    vector3 = [vector1[x]*vector2[x]  for x in xrange(len(vector1))]
    vector4 = [1 for num in vector3 if num > 0.]
    co_occur_num = sum(vector4)

    if abs(co_occur_num) <= 1e-12:
        return 0.
    
    denominator = math.log(float(len(word_list1))) + math.log(float(len(word_list2))) # 分母
    
    if abs(denominator) < 1e-12:
        return 0.
    
    return co_occur_num / denominator

def sort_words(vertex_source, edge_source, window = 2, pagerank_config = {'alpha': 0.85,}):
    """将单词按关键程度从大到小排序

    Keyword arguments:
    vertex_source   --  二维列表，子列表代表句子，子列表的元素是单词，这些单词用来构造pagerank中的节点
    edge_source     --  二维列表，子列表代表句子，子列表的元素是单词，根据单词位置关系构造pagerank中的边
    window          --  一个句子中相邻的window个单词，两两之间认为有边
    pagerank_config --  pagerank的设置
    """
    sorted_words   = []
    word_index     = {}
    index_word     = {}
    _vertex_source = vertex_source
    _edge_source   = edge_source
    words_number   = 0
    for word_list in _vertex_source:
        for word in word_list:
            if not word in word_index:
                word_index[word] = words_number
                index_word[words_number] = word
                words_number += 1

    graph = np.zeros((words_number, words_number))
    
    for word_list in _edge_source:
        for w1, w2 in combine(word_list, window):
            if w1 in word_index and w2 in word_index:
                index1 = word_index[w1]
                index2 = word_index[w2]
                graph[index1][index2] = 1.0
                graph[index2][index1] = 1.0

    if False :
        nx_graph = nx.from_numpy_matrix(graph)
        scores = nx.pagerank(nx_graph, **pagerank_config)          # this is a dict
        
        sorted_scores = sorted(scores.items(), key = lambda item: item[1], reverse=True)
        for index, score in sorted_scores:
            item = AttrDict(word=index_word[index], weight=score)
            sorted_words.append(item)
            
    return sorted_words

def sort_sentences(sentences, words, sim_func = get_similarity, pagerank_config = {'alpha': 0.85,}):
    """将句子按照关键程度从大到小排序

    Keyword arguments:
    sentences         --  列表，元素是句子
    words             --  二维列表，子列表和sentences中的句子对应，子列表由单词组成
    sim_func          --  计算两个句子的相似性，参数是两个由单词组成的列表
    pagerank_config   --  pagerank的设置
    """
    sorted_sentences = []
    _source = words
    sentences_num = len(_source)        
    graph = np.zeros((sentences_num, sentences_num))
    
    for x in xrange(sentences_num):
        for y in xrange(x, sentences_num):
            similarity = sim_func( _source[x], _source[y] )
            graph[x, y] = similarity
            graph[y, x] = similarity
    
    if False :        
        nx_graph = nx.from_numpy_matrix(graph)
        scores = nx.pagerank(nx_graph, **pagerank_config)              # this is a dict
        sorted_scores = sorted(scores.items(), key = lambda item: item[1], reverse=True)
    
        for index, score in sorted_scores:
            item = AttrDict(sentence=sentences[index], weight=score)
            sorted_sentences.append(item)

    return sorted_sentences


def get_file_sentences(filename, encoding="utf-8"):
    
    norm_sentences = None
    if (os.path.exists(filename)) :
        f = codecs.open(filename, 'r', encoding, 'ignore')
        sentences = [s for s in f if len(s.strip()) > 0]
        norm_sentences = [normalize_sentence(s) for s in sentences]
        f.close()
    
    return norm_sentences

def get_uid() :
    now = datetime.datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S%f")


def get_creation_file_date(filename):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if sys.platform == 'Win32':
        return os.path.getctime(filename)
    else:
        stat = os.stat(filename)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime



def get_sentence_type (s):
    m = re.search('^[0-9]{1,3}\s', s)
    if m :
            print ("A : " + m.group(0))
            
    m = re.search('^[0-9]{1,3}\.[\D]', s)
    if m :
            print ("Aa : " + m.group(0))
            
    m = re.search('^[0-9]{1,3}\.[0-9]{1,3}[^\.]', s)
    if m :
        if m.group(0)[-1] != ' ' :
            print ("A : " + m.group(0)[:-1])
        else :
            print ("A : " + m.group(0))
    m = re.search('^[0-9]{1,3}(\.[0-9]{1,3}){2}[^\.]', s)
    if m :
        print ("B :  " + m.group(0))
    
    # 第.... 条 title
    m = re.search('^第[\s\d一二三四五六七八九十百千\s]{1,7}条', s)
    if m :
        print ("C :  " + m.group(0))
        
    m = re.search('^[一二三四五六七八九十百千]{1,7}[\s]?[\.、]{1}', s)
    if m :
        print ("C :  " + m.group(0))
       



if __name__ == '__main__':
     

    get_sentence_type("2.1 股份公司中文名称：内蒙古蒙西水泥股份有限公司（最终以 工商登记机关核准的名称为准）；")
    get_sentence_type("2 股份公司的名称和住所")
    get_sentence_type("2.14 144规则报告。")
    get_sentence_type("1.2.2dd")
    get_sentence_type("1.3.1.3")
    get_sentence_type("1.4.6 1.5.4")
    get_sentence_type("第   1 条")
    get_sentence_type("第八百五十八条")
    get_sentence_type("八百五十八. ")
    get_sentence_type("八、")
    get_sentence_type("五  ")
    get_sentence_type("10. dd")
    get_sentence_type("11.cc")
    get_sentence_type("ss二零零二年十一月__日")
    get_sentence_type("零年 零月零日")
    get_sentence_type("2年 月日")
    get_sentence_type("2,年 ;月日")
    get_sentence_type("2年 ;月,日")
    
    # 第.... 条 title
     
     
     
    
    