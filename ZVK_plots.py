# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 12:53:52 2023

@author: huberm
"""
###############################################################################
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
###############################################################################

# import data
df = pd.read_excel("ZVK_2022_2024Q2.xlsx", sheet_name="Tabelle2") #original
#df = pd.read_excel("ZVK_2022_2024Q1.xlsx", sheet_name="Tabelle4") #für Jahre; Jahr 2023 manuell mit Simones Zahlen nachbearbeitet (sie hat davor gerundet, deshalb gibt es andere Zahlen wenn ich den mean von 2023Q1-Q4 berechne als wenn sie das macht)

# merge columns Anwendungsrate and Infektionsrate in one (Rate) + add another column in front stating the type of rate (Typ Rate)
df_melt = pd.melt(df, id_vars=['ZVK-Tage', 'ZVK Infektionen', 'Station', 'ZVK Typ', 'Jahr', 'Quartal', 'Jahr_Quartal'], value_vars=['Anwendungsrate', 'Infektionsrate'], var_name='Rate Type', value_name='Rate')

df_melt_IPSNeo = df_melt[df_melt["Station"] == 'IPS/Neo']
df_melt_IPSA = df_melt[df_melt["Station"] == 'IPSA' ]
df_melt_IPSB = df_melt[df_melt["Station"] == 'IPSB' ]
df_melt_Neo = df_melt[df_melt["Station"] == 'Neo' ]

# ///selct either Jahr_Quartal or Jahr for two different Plots !!! ///
def facetgrid_AnwendungInfektion (df:pd.DataFrame, column_timesteps, saving):
    # Convert name of respective df to a string for later use (state station within plot, name plot-file)
    station = [name for name, obj in globals().items() if obj is df][0][8:] #skip first 8 characters ('df_melt_')
    
    #remove 2022 in the case of Jahr_Quartal
    if column_timesteps == 'Jahr_Quartal':
        df = df[df['Jahr'] != 2022]
    
    # Set up the FacetGrid
    g = sns.FacetGrid(df, row="Rate Type", aspect=4, sharey=False, sharex=False) #row defines how many subplots
    
    # Map the bar plots to the FacetGrid
    g.map_dataframe(
        sns.barplot,
        x=column_timesteps,
        y="Rate",
        hue="ZVK Typ",
        palette="magma", 
        ci = None
    )
    
    # Adjust the layout
    g.fig.subplots_adjust(hspace=0.5)
    
    # Add legend outside the plot | 2nd line would shift it lower
    plt.legend(title='ZVK Typ', bbox_to_anchor=(1.13, 2.6), loc='best', borderaxespad=0, fontsize=12, title_fontsize=12)
    #plt.legend(title='ZVK Typ', bbox_to_anchor=(1.14, 1.76), loc='best', borderaxespad=0, fontsize=12, title_fontsize=12)
  
    # Set labels for axes and title
    g.set_axis_labels("Jahr", "Rate")
    #different labelling based on using Jahr_Quartal or Jahr only
    if column_timesteps == 'Jahr_Quartal':
        g.set_xticklabels(('2023 Q1', '2023 Q2', '2023 Q3', '2023 Q4', '2024 Q1', '2024 Q2'))
    else: #column_timesteps == 'Jahr'
        g.set_xticklabels(('2022', '2023', '2024 Q1+Q2'))
    g.fig.text(0.996, 1.03, station, fontsize=14, verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.3))
    #would shift Station box lower
    #g.fig.text(1.005, 0.75, station, fontsize=14, verticalalignment='top', horizontalalignment='left',
           #bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.3))
    g.fig.suptitle("ZVK: Anwendung & Infektionen", fontsize=14, y=1.04, x=0.52)
    g.axes.flatten()[0].set_title('Rate = Anwendungsrate [ZVK-Tage / 100 Patienten-Tage]')
    g.axes.flatten()[1].set_title('Rate = Infektionsrate [ZVK-Infekte / 1000 ZVK-Tage]', y=1, x=0.5)
    
    # Adjust the fontsize
    for ax in g.axes.flat:
        ax.set_title(ax.get_title(), fontsize=12)  # Adjust title font size
        ax.set_xlabel(ax.get_xlabel(), fontsize=12)  # Adjust x-label font size
        ax.set_ylabel(ax.get_ylabel(), fontsize=12)  # Adjust y-label font size
        ax.tick_params(axis='both', labelsize=12)  # Adjust tick label font size
    
    # annotate bars:
    subplot_nr=0
    bar_nr=0
    #different labelling (groupby) based on using Jahr_Quartal or Jahr only
    if column_timesteps == 'Jahr_Quartal':
        df = df
    else: #column_timesteps == 'Jahr'
        df = df.groupby(['Jahr', 'ZVK Typ', 'Rate Type'], as_index=False, sort=False).aggregate({'ZVK-Tage': 'sum', 'ZVK Infektionen': 'sum', 'Rate': lambda x: round(x.mean(), 1)})
    for ax in g.axes.flat:
        subplot_nr+=1 #for upper plot you have to subtract 10x more from height for inner annotation (absolute number)
        for i, bar in enumerate(ax.patches):
            height = bar.get_height() #extract height of bar to locate  label properly
            yaxis = ax.get_ylim()[1] #extract y-axis scale (top) of bar to correct location of  label properly
            if subplot_nr == 1:
                bar_nr+=1
                #height+(yaxis/166.7) -> first had height+0.3, but adding is dependent on scale -> y-axis=50 -> 50/0.3=166.7, this factor ok for others too
                ax.annotate(str(np.round(df['Rate'].iloc[i],1))+' %', (bar.get_x() + bar.get_width() / 2, height+(yaxis/166.7)), color='dimgrey', ha='center', va='bottom') #annotate on top of bar (percentage) 
                #ax.annotate(str(int(df['ZVK-Tage'].iloc[i])), (bar.get_x() + bar.get_width() / 2, height-7), color='seashell', ha='center', va='bottom') #annotate within bar (absolute number, in case within bar)
            else: #subplot_nr == 2
                #i = i + #bars in one row
                ax.annotate(str(np.round(df['Rate'].iloc[i+bar_nr],1)), (bar.get_x() + bar.get_width() / 2, height+(yaxis/166.7)), color='dimgrey', ha='center', va='bottom') #annotate on top of bar (percentage)
                if (height-(yaxis/7.1)) > 0: #bar long enough to annotate
                    ax.annotate(str(int(df['ZVK Infektionen'].iloc[i+bar_nr])), (bar.get_x() + bar.get_width() / 2, height-(yaxis/7.1)), color='seashell', ha='center', va='bottom') #annotate within bar (absolute number)
                else: #bar too short -> annotate higher than normally
                    ax.annotate(str(int(df['ZVK Infektionen'].iloc[i+bar_nr])), (bar.get_x() + bar.get_width() / 2, height-(yaxis/10.5)), color='seashell', ha='center', va='bottom') #annotate within bar (absolute number)
    # save figure:
    if saving == 'YES':
        #if Jahr_Quartal save as 2023Q1234_2024Q1 etc.
        #if Jahr save as 2022_2023_2024Q1 etc.
        plt.savefig('2023Q1234_2024Q12_' +station+'_Facetgrid_AnwendungInfektion.png', format='png', dpi=1200, bbox_inches="tight")

facetgrid_AnwendungInfektion(df_melt_IPSNeo,"Jahr_Quartal", 'YES')
facetgrid_AnwendungInfektion(df_melt_IPSA,"Jahr_Quartal", 'YES')
facetgrid_AnwendungInfektion(df_melt_IPSB,"Jahr_Quartal", 'YES')
facetgrid_AnwendungInfektion(df_melt_Neo,"Jahr_Quartal", 'YES')

###############################################################################
###############################################################################
'''
# import data
df = pd.read_excel("ZVK_2022_2023Q1Q2Q4.xlsx", sheet_name="Tabelle3")

# merge columns Anwendungsrate and Infektionsrate in one (Rate) + add another column in front stating the type of rate (Typ Rate)
df_melt = pd.melt(df, id_vars=['Jahr', 'Station', 'ZVK Typ'], value_vars=['Anwendungsrate', 'Infektionsrate'], var_name='Rate Type', value_name='Rate')

df_melt_IPSNeo = df_melt[df_melt["Station"] == 'IPSNeo']
df_melt_IPSA = df_melt[df_melt["Station"] == 'IPSA' ]
df_melt_IPSB = df_melt[df_melt["Station"] == 'IPSB' ]
df_melt_Neo = df_melt[df_melt["Station"] == 'Neo' ]


def facetgrid_AnwendungInfektion20102023(df:pd.DataFrame, saving):
    
    # Convert name of respective df to a string for later use (state station within plot, name plot-file)
    station = [name for name, obj in globals().items() if obj is df][0][8:] #skip first 8 characters ('df_melt_')
    
    # Set up the FacetGrid
    g = sns.FacetGrid(df, row="Rate Type", aspect=4, sharey=False, sharex=False) #row defines how many subplots
    
    # Map the bar plots to the FacetGrid
    g.map_dataframe(
        sns.lineplot,
        x="Jahr",
        y="Rate",
        marker='o'  
    )
    
    # Different color for different subplot lines:
    #subplot row 0, column 0
    line1 = g.axes[0,0].get_lines()[0] # get the relevant Line2D object (in this case there is only one, but there could be more if using hues)
    #subplot row 1, column 0
    line2 = g.axes[1,0].get_lines()[0]
    #set colors
    line1.set_color(sns.color_palette("magma")[0])
    line2.set_color(sns.color_palette("magma")[3])
    
    # Adjust the layout
    g.fig.subplots_adjust(hspace=0.5)
    
    # Add legend outside the plot | 2nd line would shift it lower
    #plt.legend(title='ZVK Typ', bbox_to_anchor=(1.13, 2.6), loc='best', borderaxespad=0, fontsize=12, title_fontsize=12)
    #plt.legend(title='ZVK Typ', bbox_to_anchor=(1.14, 1.76), loc='best', borderaxespad=0, fontsize=12, title_fontsize=12)
  
    # Set labels for axes and title
    g.set_axis_labels("Jahr", "Rate")
    g.set(xticks=(2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023))
    g.set_xticklabels(('2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023'))
    for ax, (_, sub_df) in zip(g.axes.flat, df.groupby("Rate Type")):
        ax.set_ylim(0, max(sub_df['Rate'])+(max(sub_df['Rate'])/5))
    g.fig.text(0.675, 1.03, station, fontsize=14, verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.3))
    #would shift Station box lower
    #g.fig.text(1.005, 0.75, station, fontsize=14, verticalalignment='top', horizontalalignment='left',
           #bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.3))
    g.fig.suptitle("ZVK: Anwendung & Infektionen", fontsize=14, y=1.04, x=0.52)
    g.axes.flatten()[0].set_title('Rate = Anwendungsrate [ZVK-Tage / 100 Patienten-Tage]')
    g.axes.flatten()[1].set_title('Rate = Infektionsrate [ZVK-Infekte / 1000 ZVK-Tage]', y=1, x=0.5)
    
    # Adjust the fontsize
    for ax in g.axes.flat:
        ax.set_title(ax.get_title(), fontsize=12)  # Adjust title font size
        ax.set_xlabel(ax.get_xlabel(), fontsize=12)  # Adjust x-label font size
        ax.set_ylabel(ax.get_ylabel(), fontsize=12)  # Adjust y-label font size
        ax.tick_params(axis='both', labelsize=12)  # Adjust tick label font size
    
    # Annotate each point in the line plot with the respective y-value
    for ax in g.axes.flat:
        for line in ax.lines:
            for x, y in zip(line.get_xdata(), line.get_ydata()):
                ax.text(x, y+(y/20), f'{y:.1f}', ha='center', va='bottom', color='dimgrey')
    
    # save figure:
    if saving == 'YES':
        plt.savefig('2022_2023Q1Q2Q4_' +station+'_Facetgrid_Line_AnwendungInfektion.png', format='png', dpi=1200, bbox_inches="tight")
        
facetgrid_AnwendungInfektion20102023(df_melt_IPSNeo,'') 
facetgrid_AnwendungInfektion20102023(df_melt_IPSA,'') 
facetgrid_AnwendungInfektion20102023(df_melt_IPSB,'') 
facetgrid_AnwendungInfektion20102023(df_melt_Neo,'') 
'''

    





