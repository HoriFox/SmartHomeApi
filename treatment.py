from flask import render_template, request, jsonify
import requests
from mysqlhelper import DBConnection

class Api():  
    def __init__(self, config, logger):
        self.api_config = config
        self.logger = logger

    def run_api(self):
        self.logger.info('NEW API REQUEST -->')
        json_request = request.json
        module_type = json_request['type']
        
        if module_type == 'relay':
            ip_dev = json_request['ip']
            value_relay = json_request['value']
            self.logger.info('--> [IP(%s) SWITCH] try set value = %s' % (ip_dev, value_relay))
            try:
                requests.get('http://' + ip_dev + '/relay?value=' + value_relay)
            except requests.exceptions.ConnectionError:
                self.logger.warning('[!] [IP(%s) SWITCH] warning: error-connection-ip' % (ip_dev))
                return 'error-connection-ip'
            else:
                self.logger.info('[+] [IP(%s) SWITCH] set value = %s' % (ip_dev, value_relay))
                return 'good'

        if module_type == 'sensor':
            ip_dev = json_request['ip']
            self.logger.info('--> [IP(%s) SENSOR] try get value' % (ip_dev))
            # try:
            #     requests.get('http://' + ip_dev + '/relay?value=' + value_relay)
            # except requests.exceptions.ConnectionError:
            #     return 'error-connection-ip'
            # else:
            return 'null' + ip_dev

    def root(self):
        return render_template('index.html')

    def data_transfer(self):
        json_request = request.json
        function = json_request['function']

        link_bd = DBConnection(user=self.api_config['user_mysql'], password=self.api_config['password_mysql'],
                               host=self.api_config['host_mysql'], database=self.api_config['database_mysql'])

        if function == 'get_ip_by_name':
            relayname = json_request['relayname']
            ip_json = link_bd.select('modules', where="`ModuleName` LIKE '%" + relayname + "%'", json=True)
            return jsonify(ip_json)
        if function == 'get_list_module':
            modules_json = link_bd.select('modules', json=True)
            return jsonify(modules_json)
        if function == 'set_module':
            idModule = None if json_request['id'] == 'NULL' else json_request['id']
            query = link_bd.insert('modules', True, 'ChangeTime', 
                                        ModuleId=idModule, 
                                        ModuleName=json_request['name'], 
                                        Room=json_request['room'], 
                                        ModuleIp=json_request['ip'], 
                                        ModuleType=json_request['type'])
            return query
        if function == 'delete_module':
            idModule = json_request['id']
            link_bd.delete('modules', '`ModuleId` = ' + idModule)
            return 'good'

        if function == 'get_list_plan':
            plans_json = link_bd.select('plans', json=True)
            return jsonify(plans_json)
        if function == 'set_plan':
            idPlan = None if json_request['id'] == 'NULL' else json_request['id']
            query = link_bd.insert('plans', True, 'ChangeTime', 
                                        PlanId=idPlan, 
                                        PlanDisc=json_request['disc'], 
                                        ModuleIp=json_request['ip'], 
                                        PlanDays=json_request['days'], 
                                        PlanTime=json_request['time'])
            return query
        if function == 'delete_plan':
            idPlan = json_request['id']
            link_bd.delete('plans', '`PlanId` = ' + idPlan)
            return 'good'

        return 'function not found'