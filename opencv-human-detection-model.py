import cv2

# Load pre-trained MobileNet-SSD model
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'mobilenet_iter_73000.caffemodel')

# Initialize video capture (0 for webcam or use video file)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to fetch video frame.")
        break

    # Resize frame for faster processing
    resized_frame = cv2.resize(frame, (300, 300))
    height, width = frame.shape[:2]

    # Prepare the frame as input to the network
    blob = cv2.dnn.blobFromImage(resized_frame, scalefactor=0.007843, size=(300, 300), mean=(127.5, 127.5, 127.5))
    net.setInput(blob)

    # Perform detection
    detections = net.forward()

    # Iterate over all detected objects
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence of detection
        if confidence > 0.4:  # Minimum confidence threshold
            class_id = int(detections[0, 0, i, 1])  # Class ID
            if class_id == 15:  # Class 15 corresponds to "person"
                # Get bounding box coordinates
                box = detections[0, 0, i, 3:7] * [width, height, width, height]
                (x1, y1, x2, y2) = box.astype("int")
                
                # Draw bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Person: {confidence:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame with detections
    cv2.imshow("Crowd Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
