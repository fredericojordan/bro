'''
Created on 16 de dez de 2015

@author: fvj
'''
import math
import wgparser

# temperature
# wave_height
# wave_period
# wave_direction
# wind_speed
# wind_gust
# wind_direction

TEMPERATURE_CONSTANT = 0.2
WAVE_CONSTANT = 3
WIND_CONSTANT = 0.0025

def temp_rank(temperature):
    if temperature == 'null':
        return 0;
    return 1 - math.exp(-float(temperature)*TEMPERATURE_CONSTANT)

def wave_rank(wave_height):
    if wave_height == 'null':
        return 0;
    return 1 - math.exp(-float(wave_height)*WAVE_CONSTANT)

def wind_rank(wind_speed):
    if wind_speed == 'null':
        return 0;
    return 1 - float(wind_speed)*float(wind_speed)*WIND_CONSTANT;

def rank(temperature, wave_height, wind_speed):
    temperature_rank = temp_rank(temperature)
    wave_height_rank = wave_rank(wave_height)
    wind_speed_rank = wind_rank(wind_speed)
    
    return 100*temperature_rank*wave_height_rank*wind_speed_rank;

def get_best(forecast):
    best_rank = 0
    best_rank_index = 0

    for i in range(len(forecast[wgparser.wave_height])): #FIXME
        rank_i = rank(forecast[wgparser.temperature][i], forecast[wgparser.wave_height][i], forecast[wgparser.wind_speed][i])
        if rank_i > best_rank:
            best_rank = rank_i
            best_rank_index = i
            
    best_day = { entry:forecast[entry][best_rank_index]
                for entry in forecast
                if isinstance(forecast[entry], list) and len(forecast[entry]) > best_rank_index }
    
    forecast.update(best_day)
    return forecast