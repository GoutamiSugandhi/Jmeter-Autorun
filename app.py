@app.route('/generate-jmx', methods=['POST'])
def generate_jmx():
    data = request.json

    output_file = "generated_test.jmx"

    build_jmx(
        output_jmx=output_file,
        thread_group_name=data.get("thread_group_name", "Test"),
        protocol=data.get("protocol", "https"),
        host=data.get("host"),
        request_path=data.get("request_path", "/"),
        method=data.get("method", "GET"),
        target_level=int(data.get("users", 10)),
        ramp_up=int(data.get("ramp_up", 10)),
        steps=1,
        hold=1,
        iterations=1,
        username=data.get("username", ""),
        password=data.get("password", ""),
        csv_filename=data.get("csv_file", ""),
        csv_variable_names=data.get("csv_variables", ""),
        row1_start_rps=0,
        row1_end_rps=5,
        row1_duration=60,
        row2_start_rps=5,
        row2_end_rps=5,
        row2_duration=300,
    )

    return jsonify({
        "message": "JMX generated",
        "file": output_file
    })