=========
Govee API
=========


.. image:: https://img.shields.io/pypi/status/govee_api?label=PyPi
        :target: https://pypi.org/project/govee_api

.. image:: https://img.shields.io/travis/thomasreiser/govee_api
        :target: https://travis-ci.org/thomasreiser/govee_api

.. image:: https://readthedocs.org/projects/govee_api/badge/?version=latest
        :target: https://govee_api.readthedocs.io/en/latest/?badge=latest

.. image:: https://pyup.io/repos/github/thomasreiser/govee_api/shield.svg
     :target: https://pyup.io/repos/github/thomasreiser/govee_api



Simple and minimal Govee Home API client to control Govee smart devices.


* Free software: Apache 2.0 License
* Documentation: https://govee_api.readthedocs.io.




pip install -r requirements_dev.txt



Message to Govee
----------------

We all love your products but unfortunately there is no public API. Thus, we cannot control the devices we have purchased
in our own smart home environments. I have created this library so that I can control my devices easily without the Govee
app and to help others doing this. Nobody wants to harm you, your server infrastructure or anything or anybody else. In case
you cannot accept my code to be public, please send me an e-mail to reiser.thomas@gmail.com and I will immediately shut down
this repository and will delete all artifacts from PyPi.



Features
--------

* Control Govee IOT smart devices (Bulbs, LED strips)



Approved device support
-----------------------

+------------+----------------+
| Device SKU | Approved since |
+============+================+
| Bulbs                       |
+------------+----------------+
| -none yet-                  |
+------------+----------------+
| LED strips                  |
+------------+----------------+
| H6159      | 1.0.0          |
+------------+----------------+
| H6163      | 1.0.0          |
+------------+----------------+
| String lights               |
+------------+----------------+
| -none yet-                  |
+------------+----------------+

Please test your own devices with the API and tell me the results!
In case something did not work, please provide me the RAW JSON data received via the **new device** + **device update** events.



Not yet implemented
-------------------

* Bluetooth support
* Detect which device is capable of IOT/MQTT control and which device requires Bluetooth control
* String light support



Usage
-----

See **docs/usage.rst** or **testclient.py**