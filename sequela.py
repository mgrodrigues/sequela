import json
from threading import Thread
import cx_Oracle
import time
import datetime


class TestSuite(object):
    """
    A wrapper that encapsulates all tests.
    """

    def __init__(self, tests):
        self.tests = tests


class TestCase(object):
    """
    Represent a test. A test contains two scenarii. One by node
    name is the test name
    description is the test description
    scenarri is the couple of scenarri to run on each node
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.description = kwargs.get('description', None)
        self.scenarri = kwargs.get('scenarii', None)


class Scenario(object):
    """
    Contains needed information about the scenario to run.
    node_number is the node number to run the scenario on
    iteartions is the number of times the insert must be done
    interval is the time (in seconds) to wait after an insertion
    connection is the connection string to connect to a specific node
    """

    def __init__(self, json_data):
        self.node_number = json_data['node_number']
        self.iterations = json_data['iterations']
        self.interval = json_data['interval']
        self.connection = json_data['connection']


class ScenarioThread(Thread):
    """
    A thread that will execute a scenario specified in config file.
    It holds the underlying scrnario.
    Runing the test consists in connecting to the database then looping
    'self.iterations' times.
    Inside each iteration, a query is generated then executed then the
    thread waits the amount of time specified by 'self.interval'
    The transaction is only commited at the end then open resources are released.
    """

    def __init__(self, scenario, test_name):
        Thread.__init__(self)
        self.scenario = scenario
        self.test_name = test_name

    def run(self):
        conn = cx_Oracle.connect(self.scenario.connection)
        cursor = conn.cursor()
        for i in range(0, self.scenario.iterations):
            timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
            query = "INSERT INTO JOB_EXECUTION(JOB_EXECUTION_ID, PY_DATE, SQL_DATE, NODE, TEST_NAME) VALUES(GET_EXECUTION_ID(20180224), TO_TIMESTAMP('{}', 'YYYY-MM-DD HH24:MI:SS.FF'), CURRENT_TIMESTAMP, {}, '{}' )".format(
                timestamp, self.scenario.node_number, self.test_name)
            print "[{}] [{}] : {}".format(i, self.name, query)
            cursor.execute(query)
            time.sleep(self.scenario.interval)
        cursor.close()
        conn.commit()
        conn.close()


def config_from_file(file):
    """
    Reads a json configuration file a return it as string
    :param file: the file to read config from
    :return: a dict holding the config
    """
    json_str = open(file).read()
    config = json.loads(json_str)
    return config


def parse_config(config):
    """
    Parse the config and return a TestSuite.
    :param config: the dict holding the config
    :return: The test suite containing all tests to run
    """
    tests = []
    for json_test in config['tests']:
        scenarii = []
        for json_scenarri in json_test['scenarii']:
            scenario = Scenario(json_scenarri)
            scenarii.append(scenario)
        test = TestCase(name=json_test['test_name'], description=json_test['description'], scenarii=scenarii)
        tests.append(test)
    suite = TestSuite(tests)
    return suite


def launch_tests():
    """
    Main function that will launch the configuration from json file.
    The configuration contains a list of tests. Each test contains a couple
    of scenarii.
    For every scenario in a test a thread will be created and fired
    """
    config = config_from_file("scenarri.json")
    suite = parse_config(config)
    for test in suite.tests:
        for scenario in test.scenarri:
            thread = ScenarioThread(scenario, test.name)
            thread.start()


if __name__ == '__main__':
    """ Entry point """
    launch_tests()
