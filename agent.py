from ollama import chat
from iot_tools import (
	get_sensor_status,
	read_light_sensor,
	get_latest_reading,
	cam_capture_image,
	cam_record_video
)

# Define available tools	
def sensor_status() -> str:
	"""Check the status of the BH1745 sensor.
	
	Returns:
		The BH1745's current status and timestamp
	"""
	
	return get_sensor_status()


def read_light():
	"""Read the BH1745 sensor hardware RIGHT NOW.
	
	This performs a new sensor measurement. It does NOT retrieve
	a previous measurement from the database.

	Returns:
		The newly measured Red, Green, Blue and Clear values 
		along with a measurement timestamp
	"""
	
	return read_light_sensor()


def latest_reading() -> str:
	"""Retrieve the MOST RECENTLY PREVIOUSLY STORED sensor reading.
	
	This reads from the local database. It does NOT access the BH1745
	sensor and does NOT produce a new measurement.
	
	Returns:
		The most recently stored sensor reading and its timestamp
	"""
	return get_latest_reading()

def capture_image() -> str:
	# TODO: add description for SLM
	
	return cam_capture_image()


def record_video() -> str:
	# TODO: add description for SLM
	
	return cam_record_video()


available_tools = {
	"sensor_status": sensor_status,
	"read_light": read_light,
	"latest_reading": latest_reading
	# TODO: when ready, add cam tools
}

tools = list(available_tools.values())

# TODO: when cam tools added, update sys msg
messages = [
	{
		"role": "system",
		"content": """
You are an IoT assistant running on a Raspberry Pi 5.
Use available tools to retrieve sensor information.
The available sensor is a BH1745 luminance and color sensor.

Tool rules:
- sensor_status checks the current status of the BH1745 sensor.
- read_light reads the BH1745 sensor RIGHT NOW and provides a NEW, CURRENT measurement.
- latest_reading retrieves the most recent measurement already stored in the database.

Use read_light whenever the user asks for current, presnent live, or up-to-date sensor values.
Use latest_reading only when the useer asks for the latest stored or previously recorded reading.

When the user reqeuests a current measurement, you must call read_light 
even if a previous sensor measurement is aleady available in the conversation history.

DO NOT repeat a previous sensor measurement as if it were a new current measurement.
DO NOT invent sensor measurements.
Include a measurement timestamp when available
"""
	}
]

# ~ Possible tool queries:
	# ~ "Read the light sensor and tell me its values."
	# ~ "What is the current status of the light sensor?"
	# ~ "What was the last sensor reading?"
	# ~ How has the light level changed since the last measurement?

	
def asks_for_current_reading(user_input):
	"""Check whether the user is explicitly asking for a current sensor reading."""
	
	current_words = [
		"current", "currently", "right now", "live", "present", "up-to-date", "up to date"
	]
	
	comparison_words = [
		"compare", "difference", "change", "versus", "vs", "against"
	]
	
	has_current = any(word in user_input.lower() for word in current_words)
	has_comparison = any(word in user_input.lower() for word in comparison_words)
	
	return has_current and not has_comparison


def asks_for_stored_reading(user_input):
	"""Check whether the user is explicitly asking for a stored database reading."""
	
	stored_words = [
		"latest stored", "stored reading", "database", "previous reading",
		"last reading", "previous measurement", "last measurement"
	]
	
	comparison_words = [
		"compare", "difference", "change", "versus", "vs", "against"
	]
	
	has_stored = any(word in user_input.lower() for word in stored_words)
	has_comparison = any(word in user_input.lower() for word in comparison_words)
	
	return has_stored and not has_comparison


# Conversation loop
while True:

	user_input = input("\nYou: ")
	
	if user_input.lower() in ["exit", "quit"]:
		print("Exiting agent.")
		break
		
	messages.append({
		"role": "user",
		"content": user_input
	})
	
	# Force tool call "read_light()" when user explicitly asks 
	# for current sensor values for deterministic results
	if asks_for_current_reading(user_input):
		
		result = read_light()
		
		messages.append({
			"role": "tool",
			"tool_name": "read_light",
			"content": str(result)
		})
		
		response = chat(
			model = "LiquidAI/lfm2.5-350m",
			messages = messages
		)
		
		messages.append(response.message)
		
		print("\nAgent:", response.message.content)
	
	
	# Force tool call "latest_reading()" when user explicitly asks 
	# for database values for deterministic results
	elif asks_for_stored_reading(user_input):
		
		result = latest_reading()
		
		messages.append({
			"role": "tool",
			"tool_name": "latest_reading",
			"content": str(result)
		})
		
		response = chat(
			model="LiquidAI/lfm2.5-350m",
			messages=messages
		)
		
		messages.append(response.message)
		
		print("\nAgent:", response.message.content)
	
	else:
		
		# Let SLM decide tools
		while True:

			response = chat(
				model="LiquidAI/lfm2.5-350m",
				messages=messages,
				tools=tools
			)

			messages.append(response.message)
			
			# No more tools needed; model has produced final response
			if not response.message.tool_calls:
				print("\nAgent: ", response.message.content)
				break
			
			# Execute requested tools
			for call in response.message.tool_calls:
				
				name = call.function.name
				args = call.function.arguments
				
				if name not in available_tools:
					print("Unknown tool:", name)
					continue
					
				result = available_tools[name](**args)
				
				messages.append({
					"role": "tool",
					"tool_name": name,
					"content": str(result)
				})
