#pynos
pynos is a python library for working with Brocade devices running NOS.

##Installation
*NOTE:* To pick up support for 7.2.0 install, having checked this repo out, with:
```
sudo python setup.py install
```

If you don't care about 7.2.0, the following will probably work:
```
pip install pynos
```

##Usage
The following is an example usage of pynos. Full documentation can be found
[here](http://pythonhosted.org/pynos/).

```
>>> from pprint import pprint
>>> import pynos.device
>>> conn = ('10.24.39.211', '22')
>>> auth = ('admin', 'password')
>>> dev = pynos.device.Device(conn=conn, auth=auth)
>>> dev.connection
True
>>> del dev
>>> with pynos.device.Device(conn=conn, auth=auth) as dev:
...     pprint(dev.mac_table)
[{'interface'...'mac_address'...'state'...'type'...'vlan'...}]
>>> dev.connection
False
```

##License
pynos is released under the APACHE 2.0 license. See ./LICENSE for more
information.
