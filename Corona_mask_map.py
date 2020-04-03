#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import json
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize

import folium
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
import warnings
warnings.filterwarnings(action='ignore')


# In[2]:


address=pd.DataFrame()
for i in range(1,10):
    url = "https://8oi9s0nnth.apigw.ntruss.com/corona19-masks/v1/stores/json?page=" + str(i) + '&perPage=5000'
    response = requests.get(url)
    output = json.loads(response.content)
    output_df=json_normalize(output['storeInfos'])
    
    address=pd.concat([address,output_df])

address=address.reset_index(drop=True)


# In[3]:


sales=pd.DataFrame()
output_df=pd.DataFrame()
for i in range(1,10):
    url = "https://8oi9s0nnth.apigw.ntruss.com/corona19-masks/v1/sales/json?page=" + str(i) + '&perPage=5000'
    response = requests.get(url)
    output = json.loads(response.content)
    output_df=json_normalize(output['sales'])
    sales=pd.concat([sales,output_df])
    
sales=sales.reset_index(drop=True).drop(sales.columns[[4,5,6]],axis='columns')


# In[4]:


final=pd.merge(address,sales,on='code')
final=final.dropna(how='any')


# In[5]:


final=final.reset_index(drop=True)


# In[6]:


final['remain_stat_color']=''


# In[7]:


for i in range(len(final)):
    if final['remain_stat'][i]=='plenty':
        final['remain_stat'][i] = '100개 이상'
        final['remain_stat_color'][i] = 'green'
    elif final['remain_stat'][i] == 'some':
        final['remain_stat'][i] = '30개 이상 100개 미만'
        final['remain_stat_color'][i] = 'orange'
    elif final['remain_stat'][i] =='few':
        final['remain_stat'][i] = '2개 이상 30개 미만'
        final['remain_stat_color'][i] = 'red'
    elif final['remain_stat'][i] == 'empty':
        final['remain_stat'][i] = '1개 이하'
        final['remain_stat_color'][i] = 'lightgray'
    else:
        final['remain_stat'][i] = '판매중지'
        final['remain_stat_color'][i] = 'gray'


# In[8]:


map = folium.Map(
    location=[36,128.3],
    zoom_start=7)


# In[9]:


marker_cluster = MarkerCluster().add_to(map)
for i in range(len(final)):
    folium.Marker([final['lat'][i],final['lng'][i]],
                    icon=folium.Icon(color=final['remain_stat_color'][i]),
                    popup=folium.Popup('<strong>' + final['name'][i]+'</strong><br>'+
                                       '<strong>''주소 : ''</strong>' + final['addr'][i]+ '<br>'+
                                       '<strong>''재고수량 : ''</strong>'+ final['remain_stat'][i]+'<br>'+
                                       '<strong>''입고시간 : ''</strong>' + final['stock_at'][i], max_width=500)
                 ).add_to(marker_cluster)


# In[10]:


from branca.element import Template, MacroElement

template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>마스크 잔여수량 MAP</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>마스크 수량</div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:green;opacity:0.7;'></span>100개 이상</li>
    <li><span style='background:orange;opacity:0.7;'></span>30개 이상 100개미만</li>
    <li><span style='background:red;opacity:0.7;'></span>2개 이상 30개 미만</li>
    <li><span style='background:gray;opacity:0.7;'></span>1개 이하</li>
    <li><span style='background:black;opacity:0.7;'></span>판매 중지</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

map.get_root().add_child(macro)

map.save('corona_map.html')

