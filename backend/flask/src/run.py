#!/usr/bin/env python
from clipperz import app, db

def main():
    db.create_all()
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
