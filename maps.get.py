#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import sys
from pyzabbix.api import ZabbixAPI


with open(f'{sys.path[0]}/zabbixapi.conf') as f:
    conf = dict([
        tuple(line.split('=')) for line in map(str.strip, f.readlines())
    ])


zabbix = ZabbixAPI(url=conf["ZabbixURL"], user=conf['ZabbixLogin'], password=conf['ZabbixPassword'])

maps = zabbix.map.get(output='extend', selectSelements='extend')

get_map_id_php = '''<?php
$hostid = $_POST['hostid'];

if ($hostid == '')
    $hostid = 0;

$maps_arr = array(
'''

with open(f'{sys.path[0]}/blacklist') as bl:
    black_list = {
        "names": list(map(str.strip, bl.readlines())) if bl.read() else []
    }
print(black_list["names"])

for map in maps:
    if map['name'] in black_list["names"]:
        continue
    elements = []
    if map.get('selements'):
        for elem in map['selements']:
            print(elem['elements'], map['name'])
            if elem['elements'] and elem['elements'][0].get('hostid'):
                elements.append(elem['elements'][0]['hostid'])
    get_map_id_php += f'{int(map["sysmapid"])} => {str(elements)},\n'

get_map_id_php = get_map_id_php[:-2]

get_map_id_php += '''
);

$map_id = '';

foreach ($maps_arr as $key => $value) {
    foreach ($value as $host_id){
        if ($host_id == $hostid){
            $map_id = $key;
        }
    }
}
echo $map_id;
?>
'''

with open(f'{sys.path[0]}/get_map_id.php', 'w') as f:
    f.write(get_map_id_php)
