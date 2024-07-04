# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 12:46:38 2023

@author: HUBERM
"""

###############################################################################
import seaborn as sns
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Gauge
###############################################################################

###############################################################################
###############################################################################
#aggregate data from several files if needed
def files_to_file(*files): #*args to handle an arbitrary number of arguments
    global df_all
    df_all = pd.DataFrame()
    for file in files:
        df_sub = pd.read_excel(file)
        df_all = df_all.append(df_sub, ignore_index=True)
        df_all.to_excel('202401_202406_Cleanhands.xlsx', index=False)

files_to_file('202401_202402_Cleanhands.xlsx', '202402_202403_Cleanhands.xlsx', '202403_202405_Cleanhands.xlsx')
###############################################################################
###############################################################################

#load the dataset -> one column per event, stacked bars with done/not-done
#enter: Station, Berufsgruppe; output: Abteilung, Beruf
def load_data2(path, Station, Berufsgruppe):
    global df_full, df_select, df, Beruf, Abteilung
    #extract given variable "Berufsgruppe" for later (title) -> Beruf
    if Berufsgruppe == 'care':
        Beruf = 'Pflege'
    elif Berufsgruppe == 'doc':
        Beruf = 'Ärzte'
    elif Berufsgruppe == 'others':
        Beruf = 'Andere'
    else:
        Beruf='Alle Berufe'
    #extract given variable "Station" for later (title) -> Abteilung
    Abteilung = Station if Station != '' else 'Alle Abteilungen'
    #read dataframe:
    df_full = pd.read_excel(path)
    #drop station BH E:
    df_full = df_full[df_full['Station'] != 'BH E']
    #create new column containing group of supervisor:
    df_full.loc[(df_full['Supervisor'] == "XXX") | 
                (df_full['Supervisor'] == "XXX"), 'Supervisor_group'] = 'Spitalhygiene'
    df_full.loc[(df_full['Supervisor'] == "XXX") | (df_full['Supervisor'] == "XXX") | 
                (df_full['Supervisor'] == "XXX") | (df_full['Supervisor'] == "XXX") | 
                (df_full['Supervisor'] == "XXX")| (df_full['Supervisor'] == "XXX")| 
                (df_full['Supervisor'] == "XXX") | (df_full['Supervisor'] == "XXX") |
                (df_full['Supervisor'] == "XXX"), 
                'Supervisor_group'] = 'Ärzte'
    df_full.loc[(df_full['Supervisor'] == "XXX"), 'Supervisor_group'] = 'Pflege'
    df_full['Supervisor_group'] = df_full['Supervisor_group'].fillna('Unknown')
    #df_select: df with selected Station & Beruf (if given):
    df_select = df_full
    if Abteilung != 'Alle Abteilungen': #if given Station present
        df_select = df_full.loc[(df_full['Station'] == Station)] #select rows of given Station
    if Beruf != 'Alle Berufe': #if given Beruf present
        df_select = df_full.loc[(df_full['Berufsgruppe'] == Berufsgruppe)] #select rows of given Beruf
    #df: only composed of columns Event & Aktion
    df = df_select[['Event', 'Aktion']] #select columns to be plotted -> 2
    #df = df[df.Aktion != 'non-coded'] #remove non-coded rows (not relevant unless Simone tells)
    #rename values for plotting later:
    for i in range (0, len(df)):
        if df["Event"].iat[i] == "before-pat-env":
            df["Event"].iat[i] = "Vor Patient/Umgebung"
        if df["Event"].iat[i] == "before-invasive":
            df["Event"].iat[i] = "Vor Invasiv"
        if df["Event"].iat[i] == "after-pat-env":
            df["Event"].iat[i] = "Nach Patient/Umgebung"
        if df["Event"].iat[i] == "liquids":
            df["Event"].iat[i] = "Nach Körperflüssigkeiten"
        if df["Event"].iat[i] == "non-coded":
            df["Event"].iat[i] = "Non-coded"
        df['Aktion'] = df['Aktion'].replace(['non-coded'], 'x-done')
        df['Aktion'] = df['Aktion'].replace(['not-done'], 'not done')

def HH_100(df: pd.DataFrame, saving, PNG_Name):
    global X, Y, Y_total, Y_rel, present_columns, Beruf, Abteilung
    #X: serie with Event-Aktion as group (index) & count as single column (columntitel=0)
    X = df.groupby(['Event', 'Aktion']).value_counts()
    #Y: df with Event as group (index) & done as column1 (title=done) & not-done as column2 (title=not-done)
    Y= X.to_frame() #serie->df
    Y=Y.reset_index(level=[1]) #index=column
    Y.index = Y.index.map('_'.join) if Y.index.nlevels > 1 else Y.index #if Multiindex, join
    Y = Y.pivot(columns='Aktion') #swap rows and columns
    Y.columns = [e[1] for e in Y.columns] #dupel as column header is removed (select 1, but not 0)
    Y = Y.fillna(0) #na=0
    #create a list of target events we have
    target_events = ['Non-coded', 'Nach Körperflüssigkeiten', 'Nach Patient/Umgebung', 'Vor Invasiv', 'Vor Patient/Umgebung'] #order we want; just inverted since starts from bottom
    present_events = []
    for event in target_events:
        if event in Y.index:
            present_events.append(event)
    #reset index according to desired order (inverted since it start from bottom)
    Y = Y.loc[present_events, :]
    #create a list of target actions we have
    target_actions = ['done', 'not done', 'x-done']
    present_actions = []
    for action in target_actions:
        if action in Y.columns:
            present_actions.append(action)
    #Y_total: serie with Event as group (index) & totalcount as column (columntitle=0)
    Y_total = Y[present_actions].sum(axis=1) if len(Y.columns) > 1 else Y #no summing up in case only done/only not-done (error about inexisting column)
    #alternative: Y_total = Y["done"] + Y["not done"] + Y["x-done"] if len(Y.columns) > 1 else Y
    #Y_rel: df with Event as group (index) & %done as column1 (title=done) & %not-done as column2 (title=not-done)
    Y_rel = Y[Y.columns].div(Y_total, 0)*100
    
    #plot
    sns.set_theme(style="ticks", palette="pastel")
    sns.set()
    font_color = '#525252'
    csfont = {'fontname':'Georgia'} # title font
    hfont = {'fontname':'Calibri'} # main font
    colors = ['#f47e7a', '#b71f5c', 'grey', '#dbbaa7'] #third == '#621237'
    order=present_events #reset order of categories on y-axis (inverted since it start from bottom)
    ax = Y_rel.iloc[:, 0:4].loc[order].plot.barh(align='center', stacked=True, figsize=(10, 6), color=colors)
    ax.set_ylabel("")
    plt.tight_layout()
    
    #create titel (r"$\bf{" & "}$" == bold)
    Beruf=Beruf.replace(" ", "~") #replaces empty space by tilde, so it will be perserved during following line of LaTeX math expression
    Abteilung=Abteilung.replace(" ", "~") #replaces empty space by tilde, so it will be perserved during following line of LaTeX math expression
    title = plt.title('Beobachtungen Clean Hands -- ' + r"$\bf{" + Beruf + "}$" + ' -- ' + r"$\bf{" + Abteilung + "}$" , pad=60, fontsize=18, color=font_color, **csfont)
    title.set_position([.5, 1.02])
    plt.subplots_adjust(top=0.8, left=0.26) # Adjust the subplot so that the title would fit
    
    #set font size/color for labels and ticks
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(15)
    plt.xticks(color=font_color, **hfont)
    plt.yticks(color=font_color, **hfont)
    plt.xlabel('% der Beobachtungen',color=font_color, **hfont, size=15)
       
    #create legend
    handles, labels = ax.get_legend_handles_labels() #getting handles (colors) and labels from the legend
    handles = handles[:-1] if 'x-done' in present_actions else handles[:] #remove last handle (grey) IF present
    labels = labels[:-1] if 'x-done' in present_actions else labels[:]#remove last label (x-done) IF present
    legend = plt.legend(handles, labels, loc='center', frameon=False, bbox_to_anchor=(0., 1.02, 1., .102), mode='tight', ncol=4, borderaxespad=-.46, prop={'size': 15, 'family': 'Calibri'})
    for text in legend.get_texts():
        plt.setp(text, color=font_color) 
    
    ###add number (percentage) to each sub-bar
    for n in Y:
        if n != 'x-done':
            for i, (cs, ab, pc) in enumerate(zip(Y_rel.iloc[:,:].cumsum(1)[n], Y_rel[n], Y[n])):
                if pc > 0 and ab > 8: #avoid showing 0% bars (pc>0) and numbers only next to each other when bar long enough
                    #plt.text(horizontal position, vertical position, 'text')
                    #changed all Y & Y_rel compared to function above
                    #round 2.9 -> will give you 3.0 -> int will give you 2 -> str will give you '2'
                    plt.text(cs - ab / 2, i, str(int(np.round(ab))) + '% (' + str(int(round(pc,1))) + ')', va = 'center', ha = 'center', color='w', fontsize=13, **hfont)
                elif pc > 0 and ab < 8: #if bars are shorter than 8% on top of each other
                    plt.text(cs - ab / 2, i, str(int(np.round(ab))) + '%\n(' + str(int(round(pc,1))) + ')', va = 'center', ha = 'center', color='w', fontsize=13, **hfont)
        else:
            for i, (cs, ab, pc) in enumerate(zip(Y_rel.iloc[:,:].cumsum(1)[n], Y_rel[n], Y[n])):
                if pc > 0: #avoid showing 0% bars
                    plt.text(cs - ab / 2, i, str(int(round(pc,1))), va = 'center', ha = 'center', color='w', fontsize=13, **hfont)
            
    ###add table with observers:
    df_table = df_select[["Supervisor_group"]].groupby(['Supervisor_group']).value_counts() #select only supervisor_group and group_by+count
    df_table = df_table.to_frame() #serie->df
    df_table.loc['Total'] = [df_table.sum().iloc[0]] #add new row with index 'Total' and value sum; regarding sum select only sum and no other info = .iloc[0]
    order = ['Pflege', 'Ärzte', 'Spitalhygiene', 'Unknown', 'Total']
    order = [el for el in order if el in df_table.index]
    df_table = df_table.reindex(order)
    table=plt.table(cellText=df_table.values, rowLabels=df_table.index, cellLoc='center', rowLoc='left', bbox=(-0.25, 1.02, 0.08, 0.2)) #plot table, see link for variables: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.table.html
    plt.suptitle("Beobachter:", x=0.07, y=0.99, fontsize="medium", fontweight="bold") #put title for table, see link for variables: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.suptitle.html
    
    if saving == 'YES':
        plt.savefig(PNG_Name, format='png', dpi=1800, bbox_inches="tight") #sometimes 1200 enough

###############################################################################
### RUN SCRIPT ################################################################
###############################################################################
def run_script(xlsx_name):
    station_or_berufsgruppe = ['ALL', 'IPS A', 'IPS B', 'Neo', 'doc', 'care', 'others']
    ### run first function
    for element in station_or_berufsgruppe:
        data_loaded = False
        if element == 'ALL':
            load_data2(xlsx_name, '', '')
            data_loaded = True
        else:
            if element in ('IPS A', 'IPS B', 'Neo') and df_full['Station'].eq(element).any():
                load_data2(xlsx_name, element, '')
                data_loaded = True
            elif element in ('doc', 'care', 'others') and df_full['Berufsgruppe'].eq(element).any():
                load_data2(xlsx_name, '', element)
                data_loaded = True
        ### run second function
        if data_loaded:
            HH_100(df, 'YES', f'HH_{"_".join(xlsx_name.split("_")[:2])}_{element}.png') #{"_".join(xlsx_name.split("_")[:2])} gets the fromdate_todate part of the xlsx file name

run_script('202401_202406_Cleanhands.xlsx')
###############################################################################
###############################################################################
###############################################################################

#create pyechart if needed
'''
#will take the aggregated dataframe (df_all)
from pyecharts.globals import ThemeType
percentage = df_all['Aktion'].value_counts()['done']/(df_all['Aktion'].value_counts()['done'] + df_all['Aktion'].value_counts()['not-done'])*100
percentage = np.round(percentage,1)
c = (
    Gauge(init_opts=opts.InitOpts(theme=ThemeType.LIGHT)) #MACARONS
    .add(
        "Clean Hands",
        [("", percentage)],
        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(
                color=[(0.9, "#fd666d"), (1, "#61e3c1")], width=20 #color=[(0.4, "#a51c30"), (0.8, "#fd666d")
            ),
            is_on_zero=False,  # Add this option to align the lines with the color ring
        ),
        detail_label_opts=opts.GaugeDetailOpts(
            offset_center=[0, '40%'],  # Adjust the label position
            formatter='{value}%',  # Display the value of the gauge
            font_size=28,  # Customize the font size
        ),
        axislabel_opts=opts.LabelOpts(
            distance=30,  # Adjust the distance of the labels from the center
            color='#666',  # Customize the label color
            font_size=10,  # Customize the font size
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="Gauge Charts"),
        legend_opts=opts.LegendOpts(is_show=True),
    )
    .render("gauge_JanJun2024.html")
)
'''



