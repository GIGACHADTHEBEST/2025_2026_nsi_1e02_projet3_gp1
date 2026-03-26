from controller.app_controller import AppController
from view.console_view import show_motivation

if __name__ == "__main__":
    show_motivation()

    app = AppController()
    app.run()