from front_end.app import App
from PyQt5.QtWidgets import QApplication
from general_tools.os_ops import OSInteract

if __name__ == "__main__":
    os_interact = OSInteract()
    os_interact.create_folders()
    app = QApplication([])
    main_app = None
    try:
        main_app = App()
        main_app.show()
        app.exec_()
    except Exception as e:
        # Capture the traceback for better error diagnostics.
        import traceback

        print("An error occurred:", e)
        traceback.print_exc()
    finally:
        if main_app and hasattr(main_app, "webdriver"):
            main_app.webdriver.close()
