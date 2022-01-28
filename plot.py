import matplotlib.pyplot as plt
import pandas


df = pandas.read_csv('probe (1).csv', header=0, index_col=0)


class PlotMaker:

    def __init__(self, df):
        self.df = df

    def hist(self, column):
        plt.hist(df[column], range=(1950, 2021), bins=100)
        plt.savefig(f'hist_{column}.png')

    def scatter(self, x, y):
        plt.scatter(df['year'], df['quotability'])
        plt.savefig(f'scatter.png')

    def agg(self, agg_dict, group = None, ):
        pnd_df = pandas.DataFrame()
        list_keys = []
        if group:
            pnd_df = pandas.DataFrame(self.df.groupby([group]).agg(agg_dict).reset_index())
            for key in agg_dict.keys():
                list_keys.append(key)
            self.scatter(pnd_df[list_keys[0]], pnd_df[list_keys[1]])
            plt.savefig(f'hist_agg_{group}.png')
        else:
            pnd_df = pandas.DataFrame(self.df.agg(agg_dict).reset_index())
            for key in agg_dict.keys():
                list_keys.append(key)
            self.scatter(pnd_df[list_keys[0]], pnd_df[list_keys[1]])
            plt.savefig(f'hist_ag_{list_keys[0]}.png')


plot = PlotMaker(df)
# plot.hist('year')
# plot.hist('quotability')
# plot.agg({'authors': 'count', 'quotability': 'mean'}, 'year')
# plot.agg({'year': 'mean', 'quotability': 'max'}, 'authors')
# plot.agg({'authors': 'count', 'year': 'mean'})
iey = ['АВ Шевандрин', "ЕА Петрова", "ЛЮ Богачкова", "ЕА Фокина", "ПВ Бондаренко", "ВВ Калинина", 'АВ Шипелева']
fig, ax = plt.subplots()
for name in iey:
    temp_df = df.loc[df['authors'] == name].reset_index()
    del temp_df['index']
    year = temp_df['year']
    for ye in year:
        if ye == '':
            del temp_df.loc[temp_df['year'] == ye]
    if name == "ПВ Бондаренко" or name == "ВВ Калинина":
        temp_df = temp_df.loc[temp_df['year'] > 1994]
    temp_df = temp_df.groupby(['year'])['quotability'].sum().plot(legend=True, ax=ax)


ax.legend(iey)
plt.savefig('graf.png')
# agg({'quotability': 'count', 'year': 'mean'})
# print(df.loc[df['authors'] == "АВ Шевандрин"])
# pnd_df = pandas.DataFrame(df.agg({'authors': 'count', 'year': 'mean'}).reset_index())
# print(pnd_df)
# pnd_df = pandas.DataFrame(df.groupby(['authors']).agg({'year': 'mean', 'quotability': 'max'}).reset_index())
# print(pnd_df)
# pnd_df = pandas.DataFrame(df.groupby(['year']).agg({'authors': 'count', 'quotability': 'mean'}).reset_index())
# print(pnd_df)
# plt.scatter(pnd_df['authors'], pnd_df['quotability'])
# plt.show()