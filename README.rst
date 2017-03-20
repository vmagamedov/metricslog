Essentials for application metrics collection and their submission as structured
logs.

This library also contains logging formatters to setup structured logging for
regular application logs.

Configuration examples:

- ``examples/logstash`` – send structured logs directly into `Logstash`_ via UDP
  or TCP protocol for further processing using dozens of `Logstash`_ plugins,
  among with *elasticsearch* output plugin for storing logs in `Elasticsearch`_
  and analysing them using `Kibana`_;
- ``examples/syslog`` – send structured logs using `rsyslog`_ and `CEE`_ format
  for fast and reliable logs collection and processing. With `rsyslog`_ you will
  also have ability to store logs in `Elasticsearch`_ and analyse them using
  `Kibana`_ by using *omelasticsearch* output module;
- ``examples/console`` – stream colored structured logs into *stderr*, Python
  tracebacks are also highlighted using `Pygments`_ library (if installed).

Installation
~~~~~~~~~~~~

.. code-block:: shell

    pip install metricslog

Example
~~~~~~~

Regular structured logging for application logs are possible using ``extra``
keyword argument:

.. code-block:: python

    import logging

    log = logging.getLogger('some.app.module.name')

    log.info('As you can see, %s and %s logs', 'structured', 'formatted',
             extra={'user': 123})

Logged message will be looking like this in the console:

.. code-block:: shell

    2017-01-01 00:00:00,000 INFO some.app.module.name As you can see, structured and formatted logs user=123

and like this when sent into syslog (formatted for readability):

.. code-block:: javascript

    <14>app-name: @cee: {"@timestamp": "2015-10-26T09:00:00.000Z",
                         "@version": "1",
                         "message": "As you can see, structured and formatted logs",
                         "logger": "some.app.module.name",
                         "user": 123}

.. _Logstash: https://www.elastic.co/products/logstash
.. _Elasticsearch: https://www.elastic.co/products/elasticsearch
.. _Kibana: https://www.elastic.co/products/kibana
.. _CEE: http://cee.mitre.org
.. _rsyslog: http://www.rsyslog.com
.. _Pygments: http://pygments.org
