import pymysql as pm


class Database:
    def __init__(self):
        self.conn = pm.connect(host="localhost", port=3307, user="root", password="root", database="ritcloud")
        self.cursor = self.conn.cursor()
        self.email = None
        self.status = None
        self.name = None
        self.passw = None

    def checkaccountexist(self, email):
        self.email = email
        self.status = False

        # checking if email already exist in database
        # will return zero if there is no email like this else returns 1

        exist = self.cursor.execute("select * from userinfo where email='%s'" % self.email)

        # if exist = 1 then account exist and hence new account on same cannot be created
        if exist:
            self.status = True
            self.conn.close()
        return self.status

    def setdata(self, name, email, passw):
        self.name = name
        self.email = email
        self.passw = passw

        self.cursor.execute("insert into userinfo values('%s','%s','%s')" % (name, email, passw))
        try:
            self.conn.commit()
            self.status = True
        except:
            self.conn.rollback()
            self.status = False
        finally:
            self.conn.close()
        return self.status

    def checklogin(self, email, passw):
        self.email = email
        self.passw = passw
        self.name = [[""]]

        self.cursor.execute("select * from userinfo where email='%s' and password='%s'" % (email, passw))
        if self.cursor.rowcount > 0:
            self.conn.commit()
            self.cursor.execute("select name from userinfo where email='%s' and password='%s'" % (email, passw))
            self.name = self.cursor.fetchall()
            self.status = True
        else:
            self.conn.rollback()
            self.status = False

        self.conn.close()
        return self.status, self.name[0][0]