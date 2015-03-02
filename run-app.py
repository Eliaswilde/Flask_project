import os
from app import app


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    ip = str(os.environ.get('IP','0.0.0.0'))
    if(str(os.environ.get('enviro','local')) == "staging"):
        app.run(host=ip, port=port)
    else:
        app.run()


