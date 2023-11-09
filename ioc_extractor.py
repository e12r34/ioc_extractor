import yaml, os, re
from PyPDF2 import PdfReader
from collections import Counter

class Ioc_Extractor:
    def __init__(self, configFile):
        self.configFile=configFile
        self.load_config()
        self.output=self.config['output']
    def load_config(self):
        try:
            with open(self.configFile, 'r') as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            print(e)
            exit(0)
    def load_input(self):
        self.load_filter()
        if self.config['input']['type']=='files':
            self.files=self.config['input']['location']
        elif self.config['input']['type']=='dirs':
            self.files=[]
            for dirs in self.config['input']['location']:
                files_in_dir = os.listdir(dirs)
                self.files=self.files+files_in_dir
        else:
            print('Invalid Input Type in config, just give `dirs` or `files`')
            exit(0)
        self.files = [file for file in self.files if any(file.endswith(ext) for ext in self.filter)]
    def load_filter(self):
        self.filter=self.config['filter']['extension']
    def load_pattern(self):
        self.patterns={}
        self.targets={}
        for pattern in self.config['pattern']:
            self.patterns[pattern]=re.compile(self.config['pattern'][pattern])
            self.targets[pattern]=[]
    def count_ioc(self,target,file):
        for i in target:
            for j in target[i]:
                b=open(self.output,'a')
                b.write(f'{i};{j};{target[i][j]};{file}\n')
                b.close()
    def cek_ioc(self,masukan,target):
        masukan_cek = masukan.replace('\n', '')
        for pattern in self.patterns:
            found_patterns=self.patterns[pattern].findall(masukan_cek)
            try:
                target[pattern].extend(found_patterns)
            except KeyError:
                target[pattern]=[]
                target[pattern].extend(found_patterns)
        return target
    def extracts(self,masukan=[]):
        if masukan==[]:
            for file in self.files:
                target={}
                reader = PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    target=self.cek_ioc(text,target)
                for pattern in target:
                    target[pattern]=Counter(target[pattern])
                self.count_ioc(target,file)
ioc=Ioc_Extractor(configFile='config_pattern.yml')
ioc.load_pattern()
ioc.load_input()
ioc.extracts()