# import cv2
# import face_recognition

# known_face_encodings = []
# known_face_names = []

# def add_face_encoding(image_path, name):
#     image = face_recognition.load_image_file(image_path)
#     encodings = face_recognition.face_encodings(image)
#     if encodings:
#         known_face_encodings.append(encodings[0])
#         known_face_names.append(name)
#     else:
#         print(f"No faces found in the image {name}")

# add_face_encoding(r"C:\Users\aryam\.vscode\person1.jpg", "Brad Pitt")
# add_face_encoding(r"C:\Users\aryam\.vscode\person2.jpg", "Person 2")
# add_face_encoding(r"C:\Users\aryam\.vscode\person3.jpg", "Person 3")

# video_capture = cv2.VideoCapture(0)

# while True:
#     ret, frame = video_capture.read()

#     face_locations = face_recognition.face_locations(frame)
#     face_encodings = face_recognition.face_encodings(frame, face_locations)

#     for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#         matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

#         name = "Unknown"
#         if True in matches:
#             first_match_index = matches.index(True)
#             name = known_face_names[first_match_index]

#         cv2.rectangle(frame, (left, top), (right,bottom), (0, 0, 0), 2)
#         cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

#     cv2.imshow("Video", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# video_capture.release()
# cv2.destroyAllWindows()
import os
import cv2
import face_recognition

KNOWN_FACES_DIR = "registered_users"

known_face_encodings = []
known_face_names = []

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        path = os.path.join(KNOWN_FACES_DIR, filename)
        name = os.path.splitext(filename)[0]
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(name)
        else:
            print(f"No face found in image: {filename}")

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        if True in matches:
            match_index = matches.index(True)
            name = known_face_names[match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        print("Detected:", name)

    cv2.imshow("Facial Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
