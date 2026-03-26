from controllers.app_controller import AppController
from views.console_view import show_motivation

if __name__ == "__main__":
    show_motivation()

    app = AppController()
    app.run()