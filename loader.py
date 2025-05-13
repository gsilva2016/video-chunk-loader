import threading
import queue
import time

def consumer(q):
    while True:
        print("Get item for vlm processing...")
        item = q.get(block=True, timeout=None)
        print(f"VLM Processing: {item} Started!")
        q.task_done()
        print("sleeping for vlm processing (simulation)...")
        time.sleep(30) # simulate 30 second VLM chunk processing

def rtsp_producer(q):
    print("Starting rtsp loader thread...", threading.get_ident())
    for i in range(3000):
        try:
            q.put_nowait(f"Item {i}")
            print(f"{threading.get_ident()} - Produced Chunk {i}")
            time.sleep(0.43) # guess how long it takes to create 30 second chunk?
        except queue.Full:
            print(f"{threading.get_ident()} - Queue is full! Dropping frame {i}")
            time.sleep(0.33) # time to get frame from rtsp stream 

if __name__ == "__main__":
    q = queue.Queue(maxsize=100)
   
    print("starting vlm processing thread")
    c = threading.Thread(target=consumer, args=(q,), daemon=True)
    c.start()

    # camera 1 simulation thread
    threading.Thread(target=rtsp_producer, args=(q,), daemon=True).start()

    # camera 2 simulation thread
    #threading.Thread(target=rtsp_producer, args=(q,), daemon=True).start()


    print("waiting for q processing...")
    c.join()
    print("Finished.")
