Metrics collection and submission as structured logs. And all you need to setup
structured logging for regular application logs.

Examples
~~~~~~~~

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

Issues with sending logs into Elasticsearch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Field types in Elasticsearch are static. Fields can be created dynamically, but
it's type can't be changed afterward. This means that once you indexed
``{"foo": 1}`` document into Elasticsearch, you wouldn't be able to index document
``{"foo": "bar"}``, because ``foo`` field was created with ``long`` type, which
is incompatible with ``string`` type.

In order to overcome this issue, you can use sophisticated mapping template for
Elasticsearch:

- ``examples/es2-template.yaml`` - mapping template for Elasticsearch 2.x
- ``examples/es5-template.yaml`` - mapping template for Elasticsearch 5.x

These templates are designed to treat all unknown fields as ``keyword`` type,
which can accept strings and numbers, and this field can be used for
filtering purposes. This field is actually a multi-field, with ``key``, ``num``
and ``time`` subfields, which can be used for aggregation and sorting purposes,
if the indexed value is looking like numbers or timestamps.

So, for example, when we indexed ``{"foo": "123"}`` document, we will be able to
search this fields with ``foo:123`` query and we will be able to aggregate this
field as numeric field using ``foo.num`` subfield.

**Note**: there is one more limitation in Elasticsearch, which can't be fixed by
such mapping template. Elasticseach has explicit ``object`` type, along with other
scalar types. And they all share the same namespace in the fields mapping. This
means, that if you indexed object into field ``foo``, you wouldn't be able to
index any other data type into this field, only objects. So be very careful with
what you're indexing into Elasticsearch, use objects only as namespaces with
unique and self-describing names and **prefer flat structures with scalar types**
instead of deeply nested objects.

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
