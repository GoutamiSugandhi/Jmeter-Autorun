import argparse
import os
import subprocess
import xml.etree.ElementTree as ET


def prompt_text(label, default=None, required=False):
	if default is None:
		message = f"{label}: "
	else:
		message = f"{label} [{default}]: "

	while True:
		value = input(message).strip()
		if value:
			return value
		if default is not None:
			return default
		if not required:
			return ""
		print("Value is required.")


def prompt_int(label, default):
	while True:
		value = input(f"{label} [{default}]: ").strip()
		if not value:
			return int(default)
		try:
			return int(value)
		except ValueError:
			print("Please enter a valid integer.")


def prompt_yes_no(label, default=True):
	default_text = "Y/n" if default else "y/N"
	while True:
		value = input(f"{label} [{default_text}]: ").strip().lower()
		if not value:
			return default
		if value in ("y", "yes"):
			return True
		if value in ("n", "no"):
			return False
		print("Please answer y or n.")


def resolve_jmeter_bat(explicit_path=None):
	if explicit_path:
		if os.path.isfile(explicit_path):
			return explicit_path
		print(
			f"Warning: jmeter.bat not found at '{explicit_path}'. "
			"Falling back to auto-detection."
		)

	candidates = [
		r"C:\Users\AC93847\Downloads\apache-jmeter-5.6.3\apache-jmeter-5.6.3\bin\jmeter.bat",
		r"C:\Users\AC93847\ApacheJmeter\apache-jmeter-5.6.3\bin\jmeter.bat",
		r"C:\Users\AC93847\apache-jmeter-5.6.3\bin\jmeter.bat",
		r"C:\apache-jmeter-5.6.3\bin\jmeter.bat",
		r"C:\apache-jmeter-5.6.2\bin\jmeter.bat",
		r"C:\apache-jmeter-5.6.1\bin\jmeter.bat",
	]

	for path in candidates:
		if os.path.isfile(path):
			return path

	return None


def add_hash_tree(parent):
	return ET.SubElement(parent, "hashTree")


def add_string_prop(parent, name, value):
	node = ET.SubElement(parent, "stringProp", {"name": name})
	node.text = value
	return node


def add_bool_prop(parent, name, value):
	node = ET.SubElement(parent, "boolProp", {"name": name})
	node.text = "true" if value else "false"
	return node


def build_jmx(
	output_jmx,
	thread_group_name,
	protocol,
	host,
	request_path,
	method,
	target_level,
	ramp_up,
	steps,
	hold,
	iterations,
	username,
	password,
	csv_filename,
	csv_variable_names,
	row1_start_rps,
	row1_end_rps,
	row1_duration,
	row2_start_rps,
	row2_end_rps,
	row2_duration,
):
	root = ET.Element(
		"jmeterTestPlan",
		{
			"version": "1.2",
			"properties": "5.0",
			"jmeter": "5.6.3",
		},
	)
	root_hash_tree = ET.SubElement(root, "hashTree")

	test_plan = ET.SubElement(
		root_hash_tree,
		"TestPlan",
		{
			"guiclass": "TestPlanGui",
			"testclass": "TestPlan",
			"testname": thread_group_name,
			"enabled": "true",
		},
	)
	add_string_prop(test_plan, "TestPlan.comments", "Generated from Python code")
	add_bool_prop(test_plan, "TestPlan.functional_mode", False)
	add_bool_prop(test_plan, "TestPlan.serialize_threadgroups", False)

	udv = ET.SubElement(
		test_plan,
		"elementProp",
		{
			"name": "TestPlan.user_defined_variables",
			"elementType": "Arguments",
			"guiclass": "ArgumentsPanel",
			"testclass": "Arguments",
			"testname": "User Defined Variables",
			"enabled": "true",
		},
	)
	ET.SubElement(udv, "collectionProp", {"name": "Arguments.arguments"})

	plan_hash_tree = add_hash_tree(root_hash_tree)

	thread_group = ET.SubElement(
		plan_hash_tree,
		"ThreadGroup",
		{
			"guiclass": "ThreadGroupGui",
			"testclass": "ThreadGroup",
			"testname": thread_group_name,
			"enabled": "true",
		},
	)
	main_controller = ET.SubElement(
		thread_group,
		"elementProp",
		{
			"name": "ThreadGroup.main_controller",
			"elementType": "LoopController",
			"guiclass": "LoopControlPanel",
			"testclass": "LoopController",
			"testname": "Loop Controller",
			"enabled": "true",
		},
	)
	add_bool_prop(main_controller, "LoopController.continue_forever", False)
	add_string_prop(main_controller, "LoopController.loops", str(iterations))
	add_string_prop(thread_group, "ThreadGroup.on_sample_error", "continue")
	add_string_prop(thread_group, "ThreadGroup.num_threads", str(max(1, target_level)))
	add_string_prop(thread_group, "ThreadGroup.ramp_time", str(max(1, ramp_up)))
	add_bool_prop(thread_group, "ThreadGroup.same_user_on_next_iteration", True)
	add_string_prop(thread_group, "ThreadGroup.delay", "")
	add_string_prop(thread_group, "ThreadGroup.duration", "")

	thread_group_hash_tree = add_hash_tree(plan_hash_tree)

	http_sampler = ET.SubElement(
		thread_group_hash_tree,
		"HTTPSamplerProxy",
		{
			"guiclass": "HttpTestSampleGui",
			"testclass": "HTTPSamplerProxy",
			"testname": thread_group_name,
			"enabled": "true",
		},
	)
	add_string_prop(http_sampler, "HTTPSampler.domain", host)
	add_string_prop(http_sampler, "HTTPSampler.protocol", protocol)
	add_string_prop(http_sampler, "HTTPSampler.path", request_path)
	add_bool_prop(http_sampler, "HTTPSampler.follow_redirects", True)
	add_string_prop(http_sampler, "HTTPSampler.method", method.upper())
	add_bool_prop(http_sampler, "HTTPSampler.use_keepalive", True)
	add_bool_prop(http_sampler, "HTTPSampler.postBodyRaw", False)
	sampler_args = ET.SubElement(
		http_sampler,
		"elementProp",
		{
			"name": "HTTPsampler.Arguments",
			"elementType": "Arguments",
			"guiclass": "HTTPArgumentsPanel",
			"testclass": "Arguments",
			"testname": "User Defined Variables",
			"enabled": "true",
		},
	)
	ET.SubElement(sampler_args, "collectionProp", {"name": "Arguments.arguments"})
	add_hash_tree(thread_group_hash_tree)

	header_manager = ET.SubElement(
		thread_group_hash_tree,
		"HeaderManager",
		{
			"guiclass": "HeaderPanel",
			"testclass": "HeaderManager",
			"testname": "HTTP Header Manager",
			"enabled": "true",
		},
	)
	headers = ET.SubElement(header_manager, "collectionProp", {"name": "HeaderManager.headers"})
	header = ET.SubElement(headers, "elementProp", {"name": "", "elementType": "Header"})
	add_string_prop(header, "Header.name", "Direct")
	add_string_prop(header, "Header.value", "true")
	add_hash_tree(thread_group_hash_tree)

	auth_manager = ET.SubElement(
		thread_group_hash_tree,
		"AuthManager",
		{
			"guiclass": "AuthPanel",
			"testclass": "AuthManager",
			"testname": "HTTP Authorization Manager",
			"enabled": "true",
		},
	)
	auth_list = ET.SubElement(auth_manager, "collectionProp", {"name": "AuthManager.auth_list"})
	auth = ET.SubElement(auth_list, "elementProp", {"name": "", "elementType": "Authorization"})
	add_string_prop(auth, "Authorization.url", "")
	add_string_prop(auth, "Authorization.username", username)
	add_string_prop(auth, "Authorization.password", password)
	add_string_prop(auth, "Authorization.domain", "")
	add_string_prop(auth, "Authorization.realm", "")
	add_bool_prop(auth_manager, "AuthManager.controlledByThreadGroup", False)
	add_hash_tree(thread_group_hash_tree)

	csv_data_set = ET.SubElement(
		thread_group_hash_tree,
		"CSVDataSet",
		{
			"guiclass": "TestBeanGUI",
			"testclass": "CSVDataSet",
			"testname": "CSV Data Set Config",
			"enabled": "true",
		},
	)
	add_string_prop(csv_data_set, "filename", csv_filename)
	add_string_prop(csv_data_set, "fileEncoding", "")
	add_string_prop(csv_data_set, "variableNames", csv_variable_names)
	add_bool_prop(csv_data_set, "ignoreFirstLine", True)
	add_string_prop(csv_data_set, "delimiter", ",")
	add_bool_prop(csv_data_set, "quotedData", False)
	add_bool_prop(csv_data_set, "recycle", True)
	add_bool_prop(csv_data_set, "stopThread", False)
	add_string_prop(csv_data_set, "shareMode", "shareMode.all")
	add_hash_tree(thread_group_hash_tree)

	constant_throughput_timer = ET.SubElement(
		thread_group_hash_tree,
		"ConstantThroughputTimer",
		{
			"guiclass": "TestBeanGUI",
			"testclass": "ConstantThroughputTimer",
			"testname": "Constant Throughput Timer",
			"enabled": "true",
		},
	)
	effective_rps = max(1, row2_end_rps)
	add_string_prop(
		constant_throughput_timer,
		"throughput",
		str(effective_rps * 60),
	)
	add_string_prop(constant_throughput_timer, "calcMode", "1")
	add_hash_tree(thread_group_hash_tree)

	result_collector = ET.SubElement(
		thread_group_hash_tree,
		"ResultCollector",
		{
			"guiclass": "ViewResultsFullVisualizer",
			"testclass": "ResultCollector",
			"testname": "View Results Tree",
			"enabled": "true",
		},
	)
	add_bool_prop(result_collector, "ResultCollector.error_logging", False)
	obj_prop = ET.SubElement(result_collector, "objProp")
	name_node = ET.SubElement(obj_prop, "name")
	name_node.text = "saveConfig"
	value = ET.SubElement(obj_prop, "value", {"class": "SampleSaveConfiguration"})
	for field, field_value in [
		("time", "true"),
		("latency", "true"),
		("timestamp", "true"),
		("success", "true"),
		("label", "true"),
		("code", "true"),
		("message", "true"),
		("threadName", "true"),
		("dataType", "true"),
		("encoding", "false"),
		("assertions", "true"),
		("subresults", "true"),
		("responseData", "false"),
		("samplerData", "false"),
		("xml", "false"),
		("fieldNames", "true"),
		("responseHeaders", "false"),
		("requestHeaders", "false"),
		("responseDataOnError", "false"),
		("saveAssertionResultsFailureMessage", "true"),
		("assertionsResultsToSave", "0"),
		("bytes", "true"),
		("sentBytes", "true"),
		("url", "true"),
		("threadCounts", "true"),
		("idleTime", "true"),
		("connectTime", "true"),
	]:
		child = ET.SubElement(value, field)
		child.text = field_value

	add_string_prop(result_collector, "filename", "")
	add_hash_tree(thread_group_hash_tree)

	tree = ET.ElementTree(root)
	ET.indent(tree, space="  ")
	os.makedirs(os.path.dirname(output_jmx) or ".", exist_ok=True)
	tree.write(output_jmx, encoding="utf-8", xml_declaration=True)


def main():
	parser = argparse.ArgumentParser(
		description="Create JMeter Concurrency Thread Group test case from Python code"
	)
	parser.add_argument(
		"--output-jmx",
		default=r"C:\Users\AC93847\TC15_newSampleTC.jmx",
		help="Output JMX path",
	)
	parser.add_argument(
		"--thread-group-name",
		default="TC15_newSampleTC",
		help="Concurrency Thread Group and HTTP sampler name",
	)
	parser.add_argument("--protocol", default="https", help="HTTP protocol")
	parser.add_argument("--host", default="geoese2e.test.intranet", help="Server name or IP")
	parser.add_argument(
		"--request-path",
		default=(
			"/Customer/v1/Location/postalAddressesValidations?"
			"addressLine1=${AddressLine1}&"
			"addressLine2=${AddressLine2}&"
			"locality=${Locality}&"
			"stateOrProvince=${StateOrProvince}&"
			"postCode=${PostCode}&"
			"country=${Country}&"
			"subClientId=${subClientId}"
		),
		help="HTTP request path with query string",
	)
	parser.add_argument("--method", default="GET", help="HTTP method")
	parser.add_argument("--target-level", type=int, default=1, help="Concurrency TargetLevel")
	parser.add_argument("--ramp-up", type=int, default=1, help="Concurrency RampUp")
	parser.add_argument("--steps", type=int, default=1, help="Concurrency Steps")
	parser.add_argument("--hold", type=int, default=1, help="Concurrency Hold")
	parser.add_argument("--iterations", type=int, default=1, help="Concurrency Iterations")
	parser.add_argument("--auth-user", default="geoestst", help="Authorization username")
	parser.add_argument("--auth-pass", default="h+56w7faFqrt3P@", help="Authorization password")
	parser.add_argument(
		"--csv-file",
		default=r"C:\Users\AC93847\Downloads\TC15_newSampleTC.csv",
		help="CSV file path for CSV Data Set Config",
	)
	parser.add_argument(
		"--csv-variables",
		default="AddressLine1,AddressLine2,AddressLine3,Locality,StateOrProvince,PostCode,Iso2AlphaCode,Iso3AlphaCode,Name,Country,subClientId",
		help="Comma-separated variable names for CSV Data Set Config",
	)
	parser.add_argument("--row1-start-rps", type=int, default=0, help="Throughput row1 start rps")
	parser.add_argument("--row1-end-rps", type=int, default=5, help="Throughput row1 end rps")
	parser.add_argument("--row1-duration", type=int, default=60, help="Throughput row1 duration seconds")
	parser.add_argument("--row2-start-rps", type=int, default=5, help="Throughput row2 start rps")
	parser.add_argument("--row2-end-rps", type=int, default=5, help="Throughput row2 end rps")
	parser.add_argument("--row2-duration", type=int, default=540, help="Throughput row2 duration seconds")
	parser.add_argument("--jmeter-bat", help="Optional jmeter.bat path")
	parser.add_argument(
		"--interactive",
		action="store_true",
		help="Prompt for all inputs in terminal and optionally create multiple test cases",
	)
	parser.add_argument(
		"--no-open-jmeter",
		action="store_true",
		help="Do not open JMeter GUI after creating JMX",
	)

	args = parser.parse_args()

	def launch_jmeter(jmeter_bat_hint, output_jmx):
		jmeter_bat = resolve_jmeter_bat(jmeter_bat_hint)
		if not jmeter_bat:
			raise FileNotFoundError(
				"Could not find jmeter.bat. Install JMeter or pass a valid --jmeter-bat path, "
				"e.g. C:\\Users\\AC93847\\apache-jmeter-5.6.3\\bin\\jmeter.bat"
			)
		subprocess.Popen([jmeter_bat, "-t", output_jmx])
		print(f"Opened test plan in JMeter GUI using: {jmeter_bat}")

	def create_one_case(config):
		build_jmx(
			output_jmx=config["output_jmx"],
			thread_group_name=config["thread_group_name"],
			protocol=config["protocol"],
			host=config["host"],
			request_path=config["request_path"],
			method=config["method"],
			target_level=config["target_level"],
			ramp_up=config["ramp_up"],
			steps=config["steps"],
			hold=config["hold"],
			iterations=config["iterations"],
			username=config["auth_user"],
			password=config["auth_pass"],
			csv_filename=config["csv_file"],
			csv_variable_names=config["csv_variables"],
			row1_start_rps=config["row1_start_rps"],
			row1_end_rps=config["row1_end_rps"],
			row1_duration=config["row1_duration"],
			row2_start_rps=config["row2_start_rps"],
			row2_end_rps=config["row2_end_rps"],
			row2_duration=config["row2_duration"],
		)
		print(f"Created JMX: {config['output_jmx']}")

		if not config["no_open_jmeter"]:
			launch_jmeter(config["jmeter_bat"], config["output_jmx"])

	if args.interactive:
		print("Interactive mode: create test cases grouped by suite name (any name).")
		open_jmeter_once = prompt_yes_no("Open JMeter once for each suite", not args.no_open_jmeter)
		jmeter_bat = prompt_text("jmeter.bat path (leave blank for auto-detect)", args.jmeter_bat or "")
		if not jmeter_bat:
			jmeter_bat = None

		while True:
			suite_name = prompt_text("Suite name", "SUITE_1", required=True)
			base_output_dir = os.path.dirname(args.output_jmx) or r"C:\Users\AC93847"
			default_suite_dir = os.path.join(base_output_dir, suite_name)
			suite_output_dir = prompt_text(
				f"Output folder for suite '{suite_name}'",
				default_suite_dir,
				required=True,
			)
			os.makedirs(suite_output_dir, exist_ok=True)
			suite_created_files = []

			print(f"Creating test cases for suite '{suite_name}' in: {suite_output_dir}")
			while True:
				thread_group_name = prompt_text("Thread Group name", args.thread_group_name, required=True)
				default_output = os.path.join(suite_output_dir, f"{thread_group_name}.jmx")
				output_jmx = prompt_text("Output JMX path", default_output, required=True)
				csv_default = rf"C:\Users\AC93847\Downloads\{thread_group_name}.csv"

				config = {
					"output_jmx": output_jmx,
					"thread_group_name": thread_group_name,
					"protocol": prompt_text("HTTP protocol", args.protocol, required=True),
					"host": prompt_text("Server name or IP", args.host, required=True),
					"request_path": prompt_text("HTTP request path", args.request_path, required=True),
					"method": prompt_text("HTTP method", args.method, required=True),
					"target_level": prompt_int("TargetLevel", args.target_level),
					"ramp_up": prompt_int("RampUp", args.ramp_up),
					"steps": prompt_int("Steps", args.steps),
					"hold": prompt_int("Hold", args.hold),
					"iterations": prompt_int("Iterations", args.iterations),
					"auth_user": prompt_text("Authorization username", args.auth_user, required=True),
					"auth_pass": prompt_text("Authorization password", args.auth_pass, required=True),
					"csv_file": prompt_text("CSV file path", csv_default, required=True),
					"csv_variables": prompt_text("CSV variable names", args.csv_variables, required=True),
					"row1_start_rps": prompt_int("Throughput row1 start rps", args.row1_start_rps),
					"row1_end_rps": prompt_int("Throughput row1 end rps", args.row1_end_rps),
					"row1_duration": prompt_int("Throughput row1 duration seconds", args.row1_duration),
					"row2_start_rps": prompt_int("Throughput row2 start rps", args.row2_start_rps),
					"row2_end_rps": prompt_int("Throughput row2 end rps", args.row2_end_rps),
					"row2_duration": prompt_int("Throughput row2 duration seconds", args.row2_duration),
					"jmeter_bat": jmeter_bat,
					"no_open_jmeter": True,
				}

				create_one_case(config)
				suite_created_files.append(output_jmx)

				if not prompt_yes_no(f"Create another test case in suite '{suite_name}'", False):
					break

			if open_jmeter_once and suite_created_files:
				launch_jmeter(jmeter_bat, suite_created_files[-1])
				print(
					f"Launched JMeter once for suite '{suite_name}' with latest test case: "
					f"{suite_created_files[-1]}"
				)

			if not prompt_yes_no("Create test cases for another suite", False):
				break
	else:
		create_one_case(
			{
				"output_jmx": args.output_jmx,
				"thread_group_name": args.thread_group_name,
				"protocol": args.protocol,
				"host": args.host,
				"request_path": args.request_path,
				"method": args.method,
				"target_level": args.target_level,
				"ramp_up": args.ramp_up,
				"steps": args.steps,
				"hold": args.hold,
				"iterations": args.iterations,
				"auth_user": args.auth_user,
				"auth_pass": args.auth_pass,
				"csv_file": args.csv_file,
				"csv_variables": args.csv_variables,
				"row1_start_rps": args.row1_start_rps,
				"row1_end_rps": args.row1_end_rps,
				"row1_duration": args.row1_duration,
				"row2_start_rps": args.row2_start_rps,
				"row2_end_rps": args.row2_end_rps,
				"row2_duration": args.row2_duration,
				"jmeter_bat": args.jmeter_bat,
				"no_open_jmeter": args.no_open_jmeter,
			}
		)


if __name__ == "__main__":
	main()
