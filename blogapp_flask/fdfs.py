from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin,AdminIndexView


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self,name,**kwargs):
        return redirect(url_for('login'))


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

admin = Admin(app,index_view = MyAdminIndexView())
admin.add_view(ModelView(User,db.session))
admin.add_view(ModelView(BlogPost,db.session))
