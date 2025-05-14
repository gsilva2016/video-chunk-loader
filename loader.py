import threading
import queue
import time
import cv2

def consumer(q, processing_delay=38):
    while True:
        print(f"{threading.get_ident()} - Get item for vlm processing with processing_delay {processing_delay}...")
        item = q.get(block=True, timeout=None)
        print(f"{threading.get_ident()} - VLM Processing Started for chunk: {item}")
        q.task_done()
        print(f"{threading.get_ident()} - Sleeping for vlm processing (simulation)...")
        time.sleep(processing_delay) # simulate 38 second VLM chunk processing

def rtsp_producer(q):
    rtsp_url = "rtsp://127.0.0.1:8554/camera_0"
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        print("Failed to open RTSP stream.")
        return

    print("Starting rtsp loader thread...", threading.get_ident())
    i = 0
    chunk_size = 15 * 30 # 15fps * 30 for 30second chunk
    chunkIdx = 0
    dropped_frames = 0
    while True:        
        try:
            start_time = time.time()
            ret, frame = cap.read()
            i = i + 1
            #print("Frame capture took: ", time.time()-start_time, " ms")
            #Frame capture took:  0.09931039810180664  ms
            #Frame capture took:  0.10014081001281738  ms
            #Frame capture took:  0.10012626647949219  ms
            #Frame capture took:  0.10005354881286621  ms
            #Frame capture took:  0.09984278678894043  ms

            if not ret:
                print("Stream ended or frame read error.")
                break
            if (i % chunk_size) != 0:
                continue
            chunkIdx = chunkIdx + 1

            time.sleep(0.15) # Add 15ms for write of video to disk
            q.put_nowait(f"{threading.get_ident()} - Added chunk {chunkIdx} to queue")
            print(f"{threading.get_ident()} - Produced Chunk {chunkIdx} at frame index {i}")
            # Yields ~51750ms latency between 30 second chunk generation
        except queue.Full:
            dropped_frames+=1
            print(f"{threading.get_ident()} - Queue is full! Dropping frame {i}. Total dropped: {dropped_frames}")

if __name__ == "__main__":
    q = queue.Queue(maxsize=10)
    q2 = queue.Queue(maxsize=10)
    q3 = queue.Queue(maxsize=10)
    q4 = queue.Queue(maxsize=10)
   
    print("starting vlm processing thread")
    c = threading.Thread(target=consumer, args=(q,), daemon=True)
    threading.Thread(target=consumer, args=(q2,40), daemon=True).start()
    threading.Thread(target=consumer, args=(q3,60), daemon=True).start()
    threading.Thread(target=consumer, args=(q4,75), daemon=True).start()
    c.start()

    # camera 1 simulation thread
    threading.Thread(target=rtsp_producer, args=(q,), daemon=True).start()

    # camera 2 simulation thread
    threading.Thread(target=rtsp_producer, args=(q2,), daemon=True).start()

    threading.Thread(target=rtsp_producer, args=(q3,), daemon=True).start()
    threading.Thread(target=rtsp_producer, args=(q4,), daemon=True).start()


    print("waiting for q processing...")
    c.join()
    print("Finished.")
