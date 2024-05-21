#--------------------------------------- IMPORTS -------------------------------------#
import geopy
from geopy.geocoders import Nominatim
import os,sys, json
import requests
import numpy as np

#---------------------------------- FUNCTION -----------------------------------------#
def from_name_to_cors(town_name,country):
    a_geod_code = Nominatim(user_agent='pv_gis_app')
    location = a_geod_code.geocode(f'{town_name},{country}')
    return location.latitude,location.longitude

def average_potential_and_deviation(data):
    '''
    E_d: Average daily energy production from the given system (kWh/d)
    E_m: Average monthly energy production from the given system (kWh/mo)
    H(i)_d: Average daily sum of global irradiation per square meter received by the modules of the given system (kWh/m2/d)
    H(i)_m: Average monthly sum of global irradiation per square meter received by the modules of the given system (kWh/m2/mo)
    SD_m: Standard deviation of the monthly energy production due to year-to-year variation (kWh)
    '''
    pv_potential_list,pv_deviation_list = [],[]
    for num in range(len(data)):
        pv_potential_list.append(data[num]['E_m'])
        pv_deviation_list.append(data[num]['SD_m'])

    return np.round(np.mean(pv_potential_list),decimals=2),np.round(np.mean(pv_deviation_list),decimals=2)



if __name__ =='__main__':
    CITY_NAME,COUNTRY_NAME = 'BARCELONA','SPAIN'
    LAT,LON = from_name_to_cors(town_name=CITY_NAME,country=COUNTRY_NAME)
    INSTALLED_POWER = 1 #kWp
    TECHNOLOGY  = "crystSi" # PV technology. Choices are: "crystSi", "CIS", "CdTe"
    LOSSES,LIFETIME = 14,25 # [%]
    optimal_tilt_and_angle = 1
    MOUNT="building" # building,"free"
    MAIN_URL = (f'https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat={LAT}&lon={LON}&peakpower={INSTALLED_POWER}'
f'&pvtechchoice={TECHNOLOGY}&fixed=&mountingplace={MOUNT}&loss={LOSSES}'
f'&optimalangles={optimal_tilt_and_angle}&lifetime={LIFETIME}&outputformat=json')
    response = requests.get(url=MAIN_URL)
    if response.status_code!=200:
        raise ValueError('ERROR with your request')
    try:
        data = response.json()['outputs']['monthly']['fixed']
    except Exception as e:
        print(Exception(e))
    else:
        pv_pot,pv_dev=average_potential_and_deviation(data=data)

    data_dict= {
        'PV_POTENTIAL':pv_pot,
        'PV_DEVIATION':pv_dev,
    }
## Write results in a json file on a local directory
    with open(f'./{CITY_NAME}_1.json','w') as datafile:
        json.dump(data_dict,datafile)