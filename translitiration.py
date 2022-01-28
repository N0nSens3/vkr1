#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import difflib
from pprint import pprint
from numpy import repeat, concatenate, ndarray
import pandas
import transliterate as tr
from collections import defaultdict


class NameCollector:

    names_dict = defaultdict(set)
    normalized_names_dict = defaultdict(set)

    def __init__(self, name,):
        self.name = name
        self.cyrillic_pattern = r'([А-Я])\w{1,}\s([А-Я]).\w{1,}\s([А-Яа-я]\w{1,})|([А-Я]).\w{1,}\s([А-Яа-я]\w{1,})'
        self.cyrilic_refinder_patern = r'[А=Я][А-Я]\s[А-Яа-я]\w{1,}'
        self.tranlitereted_pattern = r'([A-Z])\w{1,}\s([A-Z]).\s([A-Za-z]\w{1,})|([A-Z]).\w{1,}\s([A-Za-z]\w{1,})'
        self.matched_cyril = None
        self.matched_tranlit = None
        self.authors = None
        self.flag_invalid_cyril = False
        self.valid_cyril = False
        self.parse_name()

    def parse_name(self):
        self.matched_cyril = re.search(self.cyrillic_pattern, self.name)
        self.matched_tranlit = re.search(self.tranlitereted_pattern, self.name)
        if self.matched_cyril is None and self.matched_tranlit is not None:
            try:
                self.matched_tranlit = "".join(self.matched_tranlit[1] + self.matched_tranlit[2] + " " + self.matched_tranlit[3])
            except TypeError:
                self.matched_tranlit = "".join(self.matched_tranlit[4] + " " + self.matched_tranlit[5])
        elif self.matched_tranlit is None and self.matched_cyril is not None:
            try:
                self.matched_cyril = "".join(self.matched_cyril[1] + self.matched_cyril[2] + " " + self.matched_cyril[3])
            except TypeError:
                self.matched_cyril = "".join(self.matched_cyril[4] + " " + self.matched_cyril[5])
        elif self.matched_tranlit is None and self.matched_cyril is None:
            self.matched_cyril = self.name
        else:
            try:
                self.matched_tranlit = "".join(self.matched_tranlit[1] + self.matched_tranlit[2] + " " + self.matched_tranlit[3])
            except TypeError:
                self.matched_tranlit = "".join(self.matched_tranlit[4] + " " + self.matched_tranlit[5])
            try:
                self.matched_cyril = "".join(self.matched_cyril[1] + self.matched_cyril[2] + " " + self.matched_cyril[3])
            except TypeError:
                self.matched_cyril = "".join(self.matched_cyril[4] + " " + self.matched_cyril[5])

    def return_name(self, authors):
        self.authors = authors
        if authors is not '':
            splited_authors = authors.split(',')
            return self._author_validation(splited_authors,)
        else:
            return

    def _author_validation(self, splited_authors):
        if ord(self.authors[0]) < 128:
            if self.matched_tranlit is not None:
                name_variation = self.matched_tranlit
                self._valid_author(name_variation, splited_authors)
            else:
                self.matched_tranlit = self._complite_matches(splited_authors, self.matched_tranlit, self.matched_cyril,
                                                              True)
                if self.matched_tranlit is not None:
                    name_variation = self.matched_tranlit
                    self._valid_author(name_variation, splited_authors)
                else:
                    return self.authors
        else:
            if self.matched_cyril is not None:
                name_variation = ''
                for poten_cyril in self.matched_cyril.split(','):
                    name_variation += ","+poten_cyril if name_variation is not '' else poten_cyril
                    for name in name_variation.split(","):
                        self._valid_author(name, splited_authors)
            else:
                self.matched_cyril = self._complite_matches(splited_authors, self.matched_cyril, self.matched_tranlit,
                                                            False)
                if self.matched_cyril is not None:
                    NameCollector.names_dict[self.matched_cyril] = NameCollector.names_dict[self.matched_tranlit]
                    del NameCollector.names_dict[self.matched_tranlit]
                    name_variation = self.matched_cyril
                    for name in name_variation.split(","):
                        self._valid_author(name, splited_authors)
                else:
                    return self.authors
        return self.authors

    def _valid_author(self, name, splited_authors):
        var_name = self._compare_authors(name, splited_authors)
        if var_name is not None:
            if self.flag_invalid_cyril:
                self.matched_cyril = name
                self.flag_invalid_cyril = False
                self.valid_cyril = True
            NameCollector.names_dict[self.matched_cyril if self.matched_cyril is not None else self.matched_tranlit].add(f" {var_name}")
            return self.authors
        else:
            if self.matched_cyril is not None and self.valid_cyril is False and self.flag_invalid_cyril is False:
                for unknown_author in splited_authors:
                    if not NameCollector.names_dict[unknown_author]:
                        unknown_author = unknown_author.lstrip()
                        self.matched_cyril += "," + unknown_author if self.matched_cyril is not None \
                            else unknown_author
                        self.flag_invalid_cyril = True
            else:
                return self.authors

    def _complite_matches(self, splited_authors, empty_match, match, reversed):
        empty_match = tr.translit(match, 'ru', reversed=reversed)
        return self._compare_authors(empty_match, splited_authors)

    def _compare_authors(self, match, splited_authors):
        max_computed_similarity = 0
        valid_author = None
        for author in splited_authors:
            author = author.lstrip()
            str_comparator = difflib.SequenceMatcher(a=author, b=match)
            curr_computed_similarity = str_comparator.ratio()
            if curr_computed_similarity > max_computed_similarity and curr_computed_similarity > 0.75:
                max_computed_similarity = curr_computed_similarity
                valid_author = author
        return valid_author

    def normalized_dict_return(self):
        for k, name in NameCollector.names_dict.items():
            if NameCollector.names_dict[k]:
                NameCollector.normalized_names_dict[k] = name
        return NameCollector.normalized_names_dict


class TransducerDataFrame:

    def __init__(self, dict, df):
        self.dict = dict
        self.df = df
        self.valid_df = pandas.DataFrame()

    def transduce(self):
        self.df.drop_duplicates('title', inplace=True, ignore_index=True)
        self.valid_df = self.df.assign(authors=self.df['authors'].str.split(',')).explode('authors')
        for author in self.valid_df['authors']:
            if author is not None:
                self.valid_df.loc[self.valid_df['authors'] == author, 'authors'] = author.lstrip()
        for _, rows in self.valid_df.iterrows():
            author = rows['authors']
            self._find_name(author)
        print(self.valid_df)
        self.valid_df.to_csv('main.csv')
        return self.valid_df

    def _find_name(self, author):
        for k, values in self.dict.items():
            for value in values:
                value = value.lstrip()
                if author == value:
                    self.valid_df.loc[self.valid_df['authors'] == author, 'authors'] = k
                    return
