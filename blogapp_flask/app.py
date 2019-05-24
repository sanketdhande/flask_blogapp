from blogapp import app,login_manager

if __name__ == '__main__':
    login_manager.init_app(app)
    app.run(debug=True)
