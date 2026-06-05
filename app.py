from flask import Flask, request, jsonify

# Create app
app = Flask(__name__)

@app.route('/generate-jmx', methods=['POST'])
def generate_jmx():
    data = request.json

    return jsonify({
        "message": "JMX generated successfully",
        "input": data
    })


# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
