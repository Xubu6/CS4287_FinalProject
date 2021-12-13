import couchdb
import logging
import time
import json
import os
# import numpy
import mysql.connector
from mysql.connector import Error


class CloudifyARData:
    def __init__(self, verbose=False):
        self.setup_logging(verbose=verbose)
        self.mysql_connect()
        self.couch_connect_eva()
        self.couch_connect_iau()

    def database_exists(self, database):
        return database in self.couchserver

    def mysql_connect(self):
        """ Connect to MySQL database """
        self.mysql_db = None
        self.cursor = None
        try:
            self.mysql_db = mysql.connector.connect(host='localhost',
                                        database='ar_project',
                                        user='admin',
                                        password='password',
                                        use_pure=True)
            if self.mysql_db.is_connected():
                self.debug(
                    f"Connected to MySQL")
            self.cursor = self.mysql_db.cursor()
            self.debug(
                f"Cursor Created")
            self.cursor.execute("SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'name', name, 'img_link', img_link)) from eva;")
            self.eva_results = self.cursor.fetchall()
            self.debug(
                f"Eva Data: {self.eva_results}")
                    
            self.cursor.execute("SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'step', step, 'sub_step', sub_step, 'high_level_action', high_level_action, 'site_of_action', site_of_action, 'task_of_action', task_of_action, 'confirm_level', confirm_level, 'next_step', next_step, 'backup_step', backup_step, 'caution_level', caution_level, 'caution', caution, 'completed', completed, 'eva_id', eva_id, 'preemption_level', preemption_level, 'locked', locked)) from iau;")
            self.iau_results = self.cursor.fetchall()
            self.debug(
                f"IAU Data: {self.iau_results}")

        except Error as e:
            self.debug(f"mysql error: {e}")
        finally:
            if self.mysql_db is not None and self.mysql_db.is_connected():
                self.mysql_db.close()

    # create couchdb connection
    def couch_connect_eva(self):
        dbname = "eva"
        user = "admin"
        password = "16"
        self.couchserver = couchdb.Server("http://%s:%s@129.114.24.223:5984/" % (user, password))
        if dbname in self.couchserver:
            self.db1 = self.couchserver[dbname]
            self.debug(
                f"Successfully connected to existing CouchDB database eva")
        else:
            self.db1 = self.couchserver.create(dbname)
            self.debug(
                f"Successfully created new CouchDB database eva")
    
    # create couchdb connection
    def couch_connect_iau(self):
        dbname = "iau"
        user = "admin"
        password = "16"
        self.couchserver = couchdb.Server("http://%s:%s@129.114.24.223:5984/" % (user, password))
        if dbname in self.couchserver:
            self.db2 = self.couchserver[dbname]
            self.debug(
                f"Successfully connected to existing CouchDB database iau")
        else:
            self.db2 = self.couchserver.create(dbname)
            self.debug(
                f"Successfully created new CouchDB database iau")

    def setup_logging(self, verbose):
        self.logger = logging.getLogger('CloudifyARData')
        formatter = logging.Formatter('%(prefix)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.prefix = {'prefix': 'CloudifyARData'}
        self.logger.addHandler(handler)
        self.logger = logging.LoggerAdapter(self.logger, self.prefix)
        if verbose:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug('Debug mode enabled', extra=self.prefix)
        else:
            self.logger.setLevel(logging.INFO)

    def debug(self, msg):
        self.logger.debug(msg, extra=self.prefix)


    def get_eva_data(self):
        data = []
        cursor = self.mysql_db.cursor()
        cursor.execute("SELECT * FROM eva")
        data = cursor.fetchall()
        for row in data:
            self.debug(
                f"Row: {row}")
        return data

    def get_iau_data(self):
        data = []
        cursor = self.mysql_db.cursor()
        cursor.execute("SELECT * FROM iau")
        data = cursor.fetchall()
        for row in data:
            self.debug(
                f"Row: {row}")
        return data

    def save_to_db(self, dbname, results):
        try:
            db = self.couchserver.create(dbname)
            self.debug(
                f"Successfully created new CouchDB database {dbname}")
        except:
            db = self.couchserver[dbname]
            self.debug(
                f"Successfully connected to existing CouchDB database {dbname}")
        self.debug(f'Preparing to save results to database')

        
        res = json.dumps(results)
        data = {}
        for i, res in enumerate(results):
            data[i] = res

        db.save(data);

        # db.save(results)
        self.debug("Saving completed")

if __name__ == "__main__":
    master = CloudifyARData(verbose=True)

    eva_results = master.eva_results

    iau_results = master.iau_results

    results1 = json.dumps(eva_results)
    master.debug(f'{results1}')

    results2 = json.dumps(iau_results)
    master.debug(f'{results2}')

    # Save results to couchdb
    # master.save_to_db('eva', eva_results)
    # master.save_to_db('iau', iau_results)
    # master.save_to_db('average-load', avg_load_results)
