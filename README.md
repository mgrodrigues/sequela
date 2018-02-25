# sequela - sequence elaborated auditor

Sample python script that will evaluate the cost of having synchronization between oracle sequences in a RAC enivironment

# How it works ?

The script will read and load tests to run from a `json` configuration file.
Besides a name and description, a test is composed by many scenarii. A scenario is meant to run on a single node. 

Once tests are loaded, the script will iterate over the test list and for each will create a thread by scenario
and fire it. 

You can have as many tests as you want and each test may have as many scenarri as you want.

## The underlying test

The python script will simply do an `INSERT` statement that will insert a single row in a table which id is generated 
by calling the sequence.

The idea behind this is to run all tests twice:
* Once with a synchronied sequence
* Once without synchronized sequence

Finally an extract will be run directly on database and the two setups can be compared. 

# Prerequisites

You have a RAC configured (2+ instances). In singe node instance there is no issue with sequences synchronization 
as there is nothing to synchronize.

## Database Setup

First, prepare the database. You'll need 
* A table to insert data into
* An Oracle sequence to generate Ids

`setup.sql` contains `sql` statements to setup the database.

To create the `TABLE` run:
```oracle-sql
CREATE TABLE "SCHEMA_USERNAME"."JOB_EXECUTION"
   (
   "JOB_EXECUTION_ID" NUMBER NOT NULL ENABLE,
   "PY_DATE" TIMESTAMP (6) NOT NULL ENABLE,
   "SQL_DATE" TIMESTAMP (6) NOT NULL ENABLE,
   "NODE" VARCHAR2(100) NOT NULL ENABLE,
   "TEST_NAME" VARCHAR(200) NOT NULL ENABLE,
   CONSTRAINT "JOB_EXECUTION_PK" PRIMARY KEY ("JOB_EXECUTION_ID")
);
```
`SCHEMA_USERNAME`: Replace with your username

To create the `SEQUENCE`:

```oracle-sql
CREATE SEQUENCE SEQ_JOB_EXCUTION_ID
  START WITH 261
  MAXVALUE 9999999999999
  MINVALUE 1
  NOCYCLE
  CACHE 100
  ORDER;
```

To alter the `SEQUENCE` to disable the synchronization:
````oracle-sql
ALTER SEQUENCE SEQ_JOB_EXECUTION_ID NOORDER;
````

To create a `FUNCTION` that will use the `SEQUENCE` to generate an Id:
```oracle-sql
CREATE OR REPLACE FUNCTION get_execution_id(in_date IN NUMBER) 
    RETURN NUMBER IS execution_id NUMBER;
BEGIN
	execution_id := in_date * 1E8 + seq_job_execution_id.nextval;
	RETURN(execution_id);

END get_execution_id;
```

## Configure tests

Here is what a configuration file looks like

```json
{
  "tests": [
    {
      "test_name": "70_30_ratio",
      "description": "I couldn't care less about a proper description",
      "scenarii": [
        {
          "node_number": 1,
          "iterations": 1000,
          "interval": 1,
          "connection": "username/password@hostname:port/service_name1"
        },
        {
          "node_number": 2,
          "iterations": 300,
          "interval": 5,
          "connection": "username/password@hostname:port/service_name2"
        }
      ]
    }
  ]
}
```
Basically, a test is composed by scenarii. A scenario is run a one single node.
* `node_number` indicates the node where to run the test on.
* `iterations` is the number of time the test will be run.
* `interval` is the time to wait before two iterations.
* `connection` is the connection to string to connect to a specific node.

In the example we'll perform 1000 insertions on node 1 defined by `username/password@hostname:port/service_name1`.
After an insert is done, the program waits for 1 second before inserting anoter row.

One node 2 defined by `username/password@hostname:port/service_name2` we'll insert 300 rows. Two inserts are separed by 5 seconds.

You can configure as many tests as you want and each test can have as many scenarri as you want.

# How to run

```python
python sequela.py
```

# Results

`TODO`

