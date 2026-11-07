from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

from Business_Agent.services.excel_product_sync import sync_excel_product


# Shared OneDrive folder
EXCEL_FOLDER = Path(
    r"C:\Users\ACER\OneDrive\Business_Agent_Data"
)

# Excel workbook name
EXCEL_FILE = "Business_Data.xlsx"
class ExcelChangeHandler(FileSystemEventHandler):

    def process_excel_change(self, file_path):

        if Path(file_path).name != EXCEL_FILE:
            return

        print("\nExcel workbook changed!")
        print("File:", file_path)

        for attempt in range(5):

            try:
                time.sleep(2)

                sync_excel_product()

                break

            except PermissionError:
                print(
                    f"Excel file is locked. Retrying... "
                    f"({attempt + 1}/5)"
                )

                time.sleep(3)

            except Exception as error:
                print("Excel synchronization failed:", error)
                break

        else:
            print("Could not synchronize Excel after 5 attempts.")

    def on_modified(self, event):

        if not event.is_directory:
            self.process_excel_change(event.src_path)

    def on_created(self, event):

        if not event.is_directory:
            self.process_excel_change(event.src_path)

    def on_moved(self, event):

        if not event.is_directory:
            self.process_excel_change(event.dest_path)
            
            
def start_excel_watcher():

    event_handler = ExcelChangeHandler()
    observer = Observer()

    observer.schedule(
        event_handler,
        str(EXCEL_FOLDER),
        recursive=False
    )

    observer.start()

    print("Watching Excel folder for changes...")
    print(EXCEL_FOLDER)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping Excel watcher...")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_excel_watcher()