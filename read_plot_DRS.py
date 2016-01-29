import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator,MultipleLocator
import matplotlib.colors as colors
import matplotlib.cm as cmx
import ConfigParser
from scipy import stats
from datetime import datetime, date, time, timedelta
import sys

def plot_cracks(filename,which_site,zeroed=True):
    all_sites = []
    all_features = []
    all_num_data = []
    all_max_feature_name = []

    p_value = []
#    df=pd.read_csv(filename,sep=',',header=0,usecols=[0,1,2,3,4,5],parse_dates=[['Date','Time']],na_values=[])
    df=pd.read_csv(filename,usecols=[0,1,2,3,4,5], names=['Date', 'Time', 'Site ID', 'Feature ID', 'Reliable', 'Measurement'],parse_dates=[['Date','Time']])
#    df=df[df['Feat. Desc.']=='N']
    df=df[df['Measurement']!=' ']
    df=df[df['Measurement']!='']
    df=df[df['Measurement']!=np.nan]
    df=df[df['Date_Time']!=' ']
    df=df[df['Site ID']!=' ']
    df=df[df['Feature ID']!=np.nan]
    df['Date_Time']=pd.to_datetime(df['Date_Time'])
    df=df.dropna(subset=['Measurement'])
    print np.unique(df['Site ID'].values)

    sitelist=np.unique(df['Site ID'].values)
    fig,ax=plt.subplots(nrows=len(which_site),ncols=1,sharex=True)
    ax_ind=0
    min_date=max(df['Date_Time'])
    max_date=min(df['Date_Time'])
    

    
    for s in range(len(sitelist)):
        if sitelist[s] not in which_site:continue
        if len(which_site) != 1:
            curax=ax[ax_ind]
        else:
            curax = ax
        #getting current site and sorting according to date
        cursite=df[df['Site ID']==sitelist[s]]
        cursite.sort(['Date_Time','Feature ID'],inplace=True)
        cursite[['Measurement']]=cursite[['Measurement']].astype(float)
        print max(cursite['Date_Time'])
        print cursite.tail(20)

        if min(cursite['Date_Time'])<min_date:min_date=min(cursite['Date_Time'])
        if max(cursite['Date_Time'])>max_date:max_date=max(cursite['Date_Time'])

        print min_date, max_date

        
        all_sites.append(np.unique(cursite['Site ID'].values)[0])
        
        features=np.unique(cursite['Feature ID'].values)
        print cursite
        print features
        
        site_features = []
        site_p = []
        site_num_data = []
        site_max_feature_name = 0
        if len(features)>1:
            #generating non-repeating colors for features######## 
            jet = cm = plt.get_cmap('jet') 
            cNorm  = colors.Normalize(vmin=0, vmax=len(features)-1)
            scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
            colorVal=scalarMap.to_rgba(np.arange(len(features)))

        #generating series of markers
        marker=['x','d','+','s','*']
       
        for f in range(len(features)):
            #getting current feature
            curfeature=cursite[cursite['Feature ID']==features[f]]
            if site_max_feature_name < len(features[f]):
                site_max_feature_name = len(features[f])
            #curfeature=cursite[cursite.loc[:,'Feature ID']==features[f]]
         
            curfeature['Date_Time']=pd.to_datetime(curfeature['Date_Time'])
            
#            end_p = curfeature['Date_Time'].iloc[-1]
#            start_p = end_p - timedelta(days=7)            
#            crack_data = curfeature[curfeature['Date_Time']>=start_p]
            
            #p_value data computation
            crack_data = curfeature.tail(4)
            
            crack_data['delta'] = (crack_data['Date_Time']-crack_data['Date_Time'].values[0])
            crack_data['t'] = crack_data['delta'].apply(lambda x: x  / np.timedelta64(1,'D'))            
            
            
            data = crack_data['Measurement'].values
            time_data = crack_data['t'].values
            
            try:
                if data[-2]-data[-1] <= 1:
                    m, b, r, p, std = stats.linregress(time_data,data)            
                    site_p.append(p)
                    site_num_data.append(len(data))
                    site_features.append(np.unique(curfeature['Feature ID'].values)[0])
                    print crack_data
            except IndexError:
                print str(features[f]) + 'Index out of bounds'
            
#            for i in  np.arange(len(crack_data)):
            
            
            
            
            
            if zeroed:
                #getting zeroed displacement
                curfeature['Measurement_0']=curfeature['Measurement'].values-curfeature['Measurement'].values[0]
                #plotting zeroed displacement
                curfeature.plot('Date_Time','Measurement_0',
                                marker=marker[f%len(marker)],
                                color=colorVal[f],
                                label=features[f],
                                ax=curax)
            else:

                curfeature.plot('Date_Time','Measurement',
                                marker=marker[f%len(marker)],
                                color=colorVal[f],
                                label=features[f],
                                ax=curax)
     
        all_max_feature_name.append(site_max_feature_name)
        all_features.append(site_features)
        p_value.append(site_p)
        all_num_data.append(site_num_data)
        
        curax.set_xlabel('')
        curax.set_ylabel(sitelist[s])
        
        curax.legend(fontsize='xx-small',loc='upper left')
        ax_ind=ax_ind+1

        curax.set_xlim(min_date,max_date)
    
    fig.tight_layout()
    for i in range(len(all_sites)):
        print "\nSite: {}".format(all_sites[i])
        for k in range(all_max_feature_name[i]+21):
            sys.stdout.write('#')
        print ""
        print "# {:<{}s}     #   p value  #".format('Feature',all_max_feature_name[i])
        for k in range(all_max_feature_name[i]+21):
            sys.stdout.write('-')
        print ""
        for j in range(len(p_value[i])):
#            print str(all_features[i][j]) + '\t' + str(p_value[i][j]) +'\t'+str(all_num_data[i][j])+'\n'
            print "# {:<{}s}     #   ".format(str(all_features[i][j]),all_max_feature_name[i]) + "{:<6}   #".format(str(format(round(p_value[i][j],4),'.4f')))
        for k in range(all_max_feature_name[i]+21):
            sys.stdout.write('#')
        print ""
    
    plt.show()
    
cfg = ConfigParser.ConfigParser()
cfg.read('plotter-config.txt')  
#################################################################    
#sitelist=['Nin','Kib'] #input site code/s to plot, minimum of 2, maximum of 4
#filename='Allsites.csv' #filename of input file
#zeroed=False            #set to TRUE if you want to initial measurements at 0. 
sitelist = cfg.get('I/O','sites')
filename = cfg.get('I/O','filename')
zeroed = cfg.get('I/O','zeroed')

sitelist = sitelist.replace(' ', '')
slist = sitelist.split(',')

print "############################################################"
print "##               DEWS-L Ground Data Plotter               ##"
print "############################################################\n"

while True:
    try:
        filename = raw_input("Input filename of the allsites file: ")
        df=pd.read_csv(filename,usecols=[2], names=['Site ID'])
    except IOError:
        print "File '{}' does not exist.".format(filename)
        print "Please check the filename and try again. :)"
    else:
        break
        

df=df[df['Site ID']!=' ']
df=df.dropna()
choices = list(np.unique(df['Site ID'].values))
num_add = len(choices)%5
if num_add != 0:
    for i in range(5-num_add):
        choices.append(" ")
split = len(choices)/5
l1 = choices[0:split]
l2 = choices[split:split*2]
l3 = choices[split*2:split*3]
l4 = choices[split*3:split*4]
l5 = choices[split*4:split*5]


print "\nChoose among the following sites:"
print "########################################"
for f1, f2, f3, f4, f5 in zip(l1,l2,l3,l4,l5):
    print "## {0:<6s} {1:<6s} {2:<6s} {3:<6s} {4:<6s} ##".format(f1,f2,f3,f4,f5)
print "########################################"
print "Max of 4 sites separated by a comma. Ex. 'Nin, Bat'"

while True:
    sitelist = raw_input("Sites to be analyzed: ")
    sitelist = sitelist.replace(' ', '')
    sitelist = sitelist.title()
    slist = sitelist.split(',')
    if len(slist) > 4:
        print "{} sites chosen. Please choose only a maximum of 4 sites.".format(len(slist))
        print "Check your input and try again."
        continue
    for i in slist:
        if not (i in choices):
            print "No site '{}' in the database.".format(i)
            print "Please check you input and try again"
            break
    if not(i in choices):
        continue
    else:
        break
plot_cracks(filename,slist,zeroed)
