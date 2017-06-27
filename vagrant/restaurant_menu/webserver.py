from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/restaurants'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            page = ""
            page += "<html><body>"
            page += "<a href='/restaurants/new'>Create a new Restaurant</a>"
            restaurants = session.query(Restaurant).order_by(Restaurant.name).all()
            for restaurant in restaurants:
                page += "<h3>" + restaurant.name + "</h3>"
                page += "<a href=" + "/restaurants/" + str(restaurant.id) + "/edit>Edit</a></br>"
                page += "<a href=" + "/restaurants/" + str(restaurant.id) + "/delete>Delete</a></br>"

            page += "</body></html>"
            self.wfile.write(page)
            return
        elif self.path.endswith('/restaurants/new'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body>"
            message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'> \
                       <h2>Enter the  name of restaurant</h2> \
                       <input name='restaurantname'></input> \
                       <input type='submit' value='Submit'></input></form>"
            message += "</body></html>"
            self.wfile.write(message)
            return
        elif self.path.endswith('/edit'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            restaurant_id = int(self.path.split('/')[-2])
            restaurant = session.query(Restaurant).get(restaurant_id)
            message = ""
            message += "<html><body>"
            message += "<form method='POST' enctype='multipart/form-data' \
                       action='/restaurants/"+ str(restaurant_id) +"/edit'> \
                       <h2>Edit the  name of restaurant</h2> \
                       <input name='restaurantname' value=" + restaurant.name + "></input> \
                       <input type='submit' value='Submit'></input></form>"
            message += "</body></html>"
            self.wfile.write(message)
        elif self.path.endswith('/delete'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            restaurant_id = int(self.path.split('/')[-2])
            restaurant = session.query(Restaurant).get(restaurant_id)
            message = ""
            message += "<html><body>"
            message += "<form method='POST' enctype='multipart/form-data' \
                       action='/restaurants/"+ str(restaurant_id) +"/delete'> \
                       <h2>Are you sure about deleting" + restaurant.name + "?</h2> \
                       <input type='submit' value='Yep, Delete!'></input></form>"
            message += "</body></html>"
            self.wfile.write(message)
        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('restaurantname')
                    restaurant = Restaurant(name=message_content[0])
                    session.add(restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    message_content = fields.get('restaurantname')
                    restaurant_id = int(self.path.split('/')[-2])
                    restaurant = session.query(Restaurant).get(restaurant_id)
                    restaurant.name = message_content[0]
                    session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    restaurant_id = int(self.path.split('/')[-2])
                    restaurant = session.query(Restaurant).get(restaurant_id)
                    session.delete(restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()
if __name__ == '__main__':
    main()