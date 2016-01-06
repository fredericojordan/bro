'''
Created on 16 de dez de 2015

@author: fvj
'''
from bs4 import BeautifulSoup
import urllib2

from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor

initial_timestamp = "initstamp"
day = "hr_d"
hour = "hr_h"
timezone_id = "tzid"
temperature = "TMPE"
wave_height = "HTSGW"
wave_period = "PERPW"
wave_direction = "DIRPW"
wind_speed = "WINDSPD"
wind_gust = "GUST"
wind_direction = "SMERN" # FIXME

def parse_array(array):
    res = []
    for item in array.items:
        value = getattr(item, 'value', '')
        if isinstance(value, ast.Number):
            value = value.value
        res.append(value.encode("utf-8").replace('"', ''))
    return res

def parse_number(value):
    return float(getattr(value, 'value', ''))

def parse_unary(value):
    op = getattr(value, 'op', '')
    new_value = getattr(getattr(value, 'value', ''), 'value', '')
    return float( str(op) + str(new_value) )

def parse_str(value):
    return str(getattr(value, 'value', '')).encode("utf-8").replace('"', '')

def parse_key(key):
    return getattr(key, 'value', '').encode("utf-8").replace('"', '')

def parse_value(value):
    if isinstance(value, ast.Array):
        return parse_array(value)
    elif isinstance(value, ast.Number):
        return parse_number(value)
    elif isinstance(value, ast.UnaryOp):
        return parse_unary(value)
    else:
        return parse_str(value)

def get_forecast(link):
    html_doc = urllib2.urlopen(link).read()
    soup = BeautifulSoup(html_doc, "html.parser")
    
    forecast_text = soup.find("div", id="div_wgfcst1").find("script").string
    
    parser = Parser()
    forecast_tree = parser.parse(forecast_text)
    
    full_data = {parse_key(node.left):parse_value(node.right)
                 for node in nodevisitor.visit(forecast_tree)
                 if isinstance(node, ast.Assign)}
    
    forecast_tree = parser.parse(forecast_text)
    
    forecast = {parse_key(node.left):parse_array(node.right)
                for node in nodevisitor.visit(forecast_tree)
                if isinstance(node, ast.Assign) and isinstance(node.right, ast.Array)}
    
    full_data.update(forecast)
    return full_data