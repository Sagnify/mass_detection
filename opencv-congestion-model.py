import cv2
from datetime import datetime, timezone
import requests
import time

def get_location():
    response = requests.get('http://ip-api.com/json/')
    data = response.json()
    return data['lat'], data['lon']

lat, lon = get_location()

# Load the pre-trained MobileNet-SSD model
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'mobilenet_iter_73000.caffemodel')

cap = cv2.VideoCapture(0)  # Use webcam

last_sent_time = time.time()  # Store the time when data was last sent
send_interval = 30  # Interval in seconds (2 minutes)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to fetch video frame.")
        break

    height, width = frame.shape[:2]

    # Resize the frame for faster processing
    resized_frame = cv2.resize(frame, (300, 300))

    # Prepare input for the model
    blob = cv2.dnn.blobFromImage(resized_frame, scalefactor=0.007843, size=(300, 300), mean=(127.5, 127.5, 127.5))
    net.setInput(blob)

    detections = net.forward()

    occupied_space = 0  # Total occupied space

    # Detect people and calculate the occupied space
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.4:
            class_id = int(detections[0, 0, i, 1])
            if class_id == 15:  # "Person" class ID in MobileNet-SSD
                box = detections[0, 0, i, 3:7] * [width, height, width, height]
                x1, y1, x2, y2 = [int(coord) for coord in box]

                # Calculate area occupied by the detected person
                person_width = x2 - x1
                person_height = y2 - y1
                occupied_space += person_width * person_height  # Add to occupied space

                # Draw bounding box (optional, if you want to display it)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Calculate the total space (assuming the frame as a rectangular area)
    total_space = height * width

    # Calculate free space
    free_space = total_space - occupied_space

    # Calculate density and determine congestion level
    density = occupied_space / total_space

    if density < 0.1:
        congestion_level = "low"
    elif 0.1 <= density < 0.3:
        congestion_level = "medium"
    else:
        congestion_level = "high"

    # Prepare the data to send to the server
    data = {
        "coordinates": {
            "lat": lat,
            "lon": lon
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Using timezone-aware UTC time
        "total_area": int(total_space),  # Convert to regular int
        "occupied_space": int(occupied_space),  # Convert to regular int
        "free_space": int(free_space),  # Convert to regular int
        "density": density,
        "congestion_level": congestion_level
    }

    # Send data to server only after 2-minute interval
    current_time = time.time()
    if current_time - last_sent_time >= send_interval:
        try:
            response = requests.post("http://127.0.0.1:5000/api/crowd_data/", json=data)
            print("Response Status Code:", response.status_code)
            print("Response Text:", response.text)  # Print the response text for debugging
            if response.status_code == 201:
                print("Data sent successfully!")
            else:
                print(f"Failed to send data with status code {response.status_code}.")
        except Exception as e:
            print(f"Error sending data: {e}")
        last_sent_time = current_time  # Update the time when the data was last sent

    # Display the frame with congestion level (optional)
    cv2.putText(frame, f"Congestion: {congestion_level}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Crowd Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
