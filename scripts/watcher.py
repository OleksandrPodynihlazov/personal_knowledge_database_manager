import time
from watchdog.events import FileSystemEventHandler  # type: ignore
from watchdog.observers import Observer  # type: ignore


class Watcher(FileSystemEventHandler):
    def on_any_event(self, event):
        print(f"Event type {event.event_type} occured on {event.src_path}")


event_hander = Watcher()
observer = Observer()
observer.schedule(event_hander, path='.', recursive=False)
observer.start()
print("Started watching current directory for changes...")
time.sleep(10)

observer.stop()
observer.join()
