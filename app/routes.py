import sqlite3
from app import app
from flask import render_template, request, escape
from flask import g
from datetime import datetime
from datetime import timedelta


DATABASE = "monitor.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.commit()
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/", methods=["POST", "GET"])
@app.route("/index")
def index():
    if request.method == "POST":
        if request.form["action"] == "Claim":
            query_db(
                "update env2 set taken_by='{}', status = 1, comment=\"{}\", updated_at = CURRENT_TIMESTAMP where name = '{}'".format(
                    request.form["name"], request.form["comment"].replace('"', ''), request.form["env"]
                )
            )
        elif request.form["action"] == "Free!":
            query_db(
                "update env2 set taken_by='', status = 0, comment='', updated_at = CURRENT_TIMESTAMP where name = '{}'".format(
                    request.form["env"]
                )
            )
    env = query_db("select * from env2")
    result = []
    for envi in env:
        diff = datetime.utcnow() - datetime.strptime(envi[3], "%Y-%m-%d %H:%M:%S")
        envi = list(envi)
        envi.append(
            "{} days {} hours {} minutes".format(
                diff.days, diff.seconds // 3600, diff.seconds % 3600 // 60
            )
        )
        result.append(envi)
    # for i in result:
    #     print(i)
    return render_template("base.html", env=result)
