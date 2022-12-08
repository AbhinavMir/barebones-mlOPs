from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
from flask import Flask, request

feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

app = Flask(__name__)


class Metadata:
    busy = False

    @app.route("/isBusy", methods=['GET'])
    def isBusy(cls):
        return str(Metadata.busy)


@app.route("/", methods=['POST'])
def imagenet():
    if request.method == "POST":
        Metadata.busy = True
        image = Image.open(request.form['myImage'])
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits

        # predicts one of the 1000 ImageNet classes
        predicted_class_idx = logits.argmax(-1).item()
        prediction = model.config.id2label[predicted_class_idx]
        Metadata.busy = False
        return prediction
    print("Server Listening")


@app.route("/test", methods=['GET'])
def test():
    if Metadata.isBusy:
        return "503"
    else:
        return "200"


if __name__ == '__main__':
    app.run()

# print_lock = threading.Lock()
# import socket
# from _thread import start_new_thread
# import threading
# def threaded(c):
#     while True:
#         # Get Data from Client
#         data = c.recv(4096)
#         if not data:
#             print_lock.release()
#             break
#
#         # Use Image URL to keep
#         image = Image.open(requests.get(data, stream=True).raw)
#         inputs = feature_extractor(images=image, return_tensors="pt")
#         outputs = model(**inputs)
#         logits = outputs.logits
#
#         # Model predicts one of 21,841 classes
#         predicted_class_idx = logits.argmax(-1).item()
#         prediction = model.config.id2label[predicted_class_idx]
#
#         # Send Back Data
#         c.send(prediction)
#
#     c.close()
#
#
# def main():
#     port = 12345
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind((socket.gethostname, port))
#     server_socket.listen(5)
#
#     while True:
#         c, addr = server_socket.accept()
#         print_lock.acquire()
#
#         # Start new Thread and return id
#         start_new_thread(threaded, (c,))
#     server_socket.close()
