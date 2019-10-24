# tcp_proxy
A reimplementation of the TCP proxy from Black Hat Python. 

##  Running
Only uses vanilla python libraries, so can be run with a default python 3 install

## Options

* `-c, --client` - IP interface to bind the server to
* `-o, --client-port` - Port for the server to bind to
* `-t, --target` - Remote server address to proxy to
* `-p, --port` - Target server port to proxy to
* `-r, --receive-first` - In the book, but unused because of implementation