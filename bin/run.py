#!flask/bin/python
from app import app
import optparse



__port = 701

def getPort(value):
    return (__port, value)[value > 0]

def tornado(option, opt_str, value, parser):
    print('Tornado on port {port}...'.format(port=getPort(value)))
    from tornado.wsgi import WSGIContainer
    from tornado.httpserver import HTTPServer
    from tornado.ioloop import IOLoop

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(getPort(value))
    IOLoop.instance().start()

def builtin(option, opt_str, value, parser):
    print('Built-in development server on port {port}...'.format(port=getPort(value)))
    app.run(host="localhost",port=getPort(value),debug=True)


def main():
    parser = optparse.OptionParser(usage="%prog [options]  or type %prog -h (--help)")
    parser.add_option('--tornado', help='Tornado non-blocking web server', action="callback", callback=tornado,type="int");
    parser.add_option('--builtin', help='Built-in Flask web development server', action="callback", callback=builtin, type="int");
    (options, args) = parser.parse_args()
    parser.print_help()

if __name__ == "__main__":
    main()