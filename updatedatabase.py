import pymysql as pm


class UpdateDatabase():
    def __init__(self):
        self.conn = pm.connect(host='localhost', port=3307, user='root', password='root', database='ritcloud')
        self.cursor = self.conn.cursor()

    def updatepass(self, passw, email):
        self.cursor.execute('update userinfo set password = "%s" where email= "%s"' % (passw, email))

        try:
            self.conn.commit()
            return True
        except:
            self.conn.rollback()
            return False
        finally:
            self.conn.close()
