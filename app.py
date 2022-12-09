from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
from flask import Flask, request

feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-224')
model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

app = Flask(__name__)


class Metadata:
    busy = False

    @app.route("/isBusy", methods=['GET'])
    def isBusy():
        return str(Metadata.busy)


@app.route("/", methods=['POST'])
def imagenet():
    if request.method == "POST":
        Metadata.busy = True
        image = Image.open(request.files['myImage'])
        inputs = feature_extractor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits

        # predicts one of the 1000 ImageNet classes
        predicted_class_idx = logits.argmax(-1).item()
        prediction = model.config.id2label[predicted_class_idx]
        Metadata.busy = False
        return prediction
    print("Server Listening")


@app.route("/", methods=["GET"])
def main():
    Metadata.busy = False
    return "200: Connection Init"


@app.route("/test", methods=['GET'])
def test():
    if Metadata.busy:
        return "503"
    else:
        return "200"


if __name__ == '__main__':
    app.run()
