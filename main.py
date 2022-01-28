import re
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import pandas
# import matplotlib.pyplot as plt
# import seaborn as sns
import translitiration
import consts


class ParserGoogleScholar:

    def __init__(self, url):
        self.url = url
        self.headers = consts.HEADERS
        self.host = consts.HOST
        self.pattern = consts.PATTERN

    def _get_html(self, url, ):
        r = requests.get(url, headers=self.headers,)
        return r

    def _show_more_parse(self, url):
        cstart = '20'
        pagesize = '80'
        flag = True
        list_urls = [url]
        while flag:
            r = requests.get(url=url)
            soup = BeautifulSoup(r.text, 'html.parser')
            item = soup.find('div', id='gsc_bpf')
            disabled = item.find('button', id='gsc_bpf_more').get('disabled')
            if disabled == "":
                flag = False
            else:
                url = f"{url}&cstart={cstart}&pagesize={pagesize}"
                cstart = '100' if cstart == '20' else str(int(cstart)+100)
                pagesize = '100'
                p = requests.post(url=url)
                list_urls.append(url)
        return list_urls

    def _get_content(self, urls):
        main_df = pandas.DataFrame()
        temp_df = pandas.DataFrame(columns=['title', 'authors', 'link', 'quotability', 'year'])
        html = self._get_html(urls[0])
        soup = BeautifulSoup(html.text, 'html.parser')
        name = soup.find('head').find_next('title').get_text()
        valid_author = translitiration.NameCollector(name=name, )
        for url in urls:
            html = self._get_html(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find_all('tr', class_='gsc_a_tr')
            articles = []
            for item in items:
                title = item.find('td', class_='gsc_a_t').find_next('a', class_='gsc_a_at').get_text()
                link = consts.HOST + item.find('td', class_='gsc_a_t').find_next('a', class_='gsc_a_at').get("data-href")
                authors = item.find('td', class_='gsc_a_t').find_next('div', class_='gs_gray').get_text()
                year = item.find('td', class_='gsc_a_y').find_next('span', class_='gsc_a_h gsc_a_hc gs_ibl').get_text()
                if authors.endswith('...'):
                    link_full_authors = link
                    html_authors = self._get_html(link_full_authors)
                    soup_auth = BeautifulSoup(html_authors.text, 'html.parser')
                    item_many_auth= soup_auth.find('div', class_='gs_scl').find_next('div', class_='gsc_vcd_value')
                    authors = item_many_auth.get_text()
                authors = valid_author.return_name(authors)
                try:
                    quotability = item.find('td', class_='gsc_a_c').find_next('a', class_='gsc_a_ac gs_ibl').get_text()
                except AttributeError:
                    quotability = item.find('td', class_='gsc_a_c').find_next('a', class_='gsc_a_ac gs_ibl gsc_a_acm').get_text()
                articles.append([title, authors, link, quotability, year])
            df_articles = pandas.DataFrame(articles, columns=['title', 'authors', 'link', 'quotability', 'year'])
            main_df = temp_df.append(df_articles, ignore_index=True)
            temp_df = main_df
            print(f"Collecting {name}")
        return main_df

    def parse(self):
        result = self._parse_authors(self.url)
        print(result)
        return result

    def _page_swapper(self, url):
        html = self._get_html(url)
        soup = BeautifulSoup(html.text, 'html.parser')
        item = soup.find('div', class_='gs_scl', id='gsc_authors_bottom_pag')
        try:
            next_link = item.find('div', class_='gsc_pgn', )
            button = next_link.find('button', class_='gs_btnPR gs_in_ib gs_btn_half gs_btn_lsb gs_btn_srt gsc_pgn_pnx').get('onclick')
        except AttributeError:
            return False
        if button is not None:
            location = re.search(self.pattern, button)
            location = location[1].encode('utf-8').decode('unicode_escape')
        else:
            return False
        return consts.HOST + location

    def _parse_authors(self, url):
        temp_df = pandas.DataFrame(columns=['title', 'authors', 'link', 'quotability', 'year'])
        while url is not False:
            html = self._get_html(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find_all('div', class_='gsc_1usr')
            authors = []
            for item in items:
                author_div = item.findChildren('div', class_='gs_ai gs_scl gs_ai_chpr')
                for link in author_div:
                    authors_link = link.find('a', class_='gs_ai_pho').get('href')
                    authors.append(authors_link)
            for author in authors:
                list_urls = self._show_more_parse(self.host+author)
                df_articles = temp_df.append(self._get_content(list_urls), ignore_index=True)
                temp_df = df_articles
                print(df_articles)
            url = self._page_swapper(url)
        return df_articles


if __name__ == '__main__':
    translitiration.NameCollector.names_dict.clear()
    parser = ParserGoogleScholar(consts.URL)
    df = parser.parse()
    print(df)
    # pprint(translitiration.NameCollector.normalized_names_dict)
    # tranducer = translitiration.TransducerDataFrame(translitiration.NameCollector.normalized_names_dict, df)
    # main_df = tranducer.transduce()
    # print(main_df)