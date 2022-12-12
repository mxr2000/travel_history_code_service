from typing import Tuple, List

from flask import Flask, jsonify, request
import json


class Model:
    show_explanation: bool
    places: List[Tuple[str, bool]]

    def __init__(self, places: List[Tuple[str, bool]], show_explanation):
        self.places = places
        self.show_explanation = show_explanation

    def get_result(self) -> str:
        result = ""
        is_first = True
        for pair in self.places:
            if not is_first:
                result += '，'
            result += pair[0]
            if pair[1]:
                result += '*'
            is_first = False
        if self.show_explanation:
            result += '（住：*表示当前城市存在中风险或高风险地区，并不表示用户实际到访过这些中高风险地区）'
        return result


app = Flask(__name__)


def read_json_file() -> Model:
    content = ""
    with open('data.json', 'r') as file:
        for line in file:
            content += line
    raw = json.loads(content)
    pairs_raw = raw["pairs"]
    show_explanation = raw["show_explanation"]
    pairs: List[Tuple[str, bool]] = []
    for pair_raw in pairs_raw:
        pairs.append((pair_raw["place"], pair_raw["show_asteroid"]))

    return Model(pairs, show_explanation)


def write_into_json(model: Model):
    result = {"show_explanation": model.show_explanation, "pairs": []}
    for pair in model.places:
        result["pairs"].append({
            "place": pair[0],
            "show_asteroid": pair[1]
        })
    with open('data.json', 'w') as file:
        file.write(json.dumps(result))



@app.get("/places")
def get_places():
    model = read_json_file()
    resp = {
        "pairs": [],
        "show_explanation": model.show_explanation

    }
    for pair in model.places:
        resp["pairs"].append({
            "place": pair[0],
            "show_asteroid": pair[1]
        })
    return jsonify(resp)


@app.get("/result")
def get_result():
    model = read_json_file()
    return model.get_result()


@app.post("/places")
def update_places():
    if request.content_type != "application/json":
        return "Error format", 400
    req = request.json
    show_explanation = req["show_explanation"]
    model = Model([], False)
    model.show_explanation = show_explanation
    model.places = []
    for pair in req["pairs"]:
        place = pair["place"]
        show_asteroid = pair["show_asteroid"]
        model.places.append((place, show_asteroid))
    write_into_json(model)
    return "ok", 200


def after_request(response):
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response


app.after_request(after_request)


if __name__ == '__main__':
    app.run(port=8080)