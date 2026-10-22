from ollama import chat
from agent_tools import (
    get_sensor_status,
    read_light_sensor,
    get_latest_sensor_reading,
    get_latest_camera_metadata,
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


def latest_sensor_reading() -> str:
    """Retrieve the MOST RECENTLY STORED BH1745 sensor reading.

    This reads from the local sensor database (sensor_db). 
    It does NOT access the BH1745 sensor and does NOT produce a new measurement.

    Returns:
            The most recently stored sensor reading and its timestamp
    """

    return get_latest_sensor_reading()


def latest_camera_metadata() -> str:
    """Retrieve the metadata for the MOST RECENTLY STORED image or video.

    This reads from the local camera database (camera_db). 
    It does NOT access the camera and does NOT produce new metadata or media.

    Returns:
            The metadata for the most recently stored image or video
            including type, timestamp, and filename
    """

    return get_latest_camera_metadata()


def capture_image() -> str:
    """Capture a still image using the camera RIGHT NOW.

    This uses the Raspberry Pi Camera Module 3 to capture a still image.
    It does NOT retrieve previous metadata from the database.

    Returns:
            The newly captured image's metadata: 
            SOURCE, TYPE, TIMESTAMP, and FILE_NAME
    """

    return cam_capture_image()


def record_video() -> str:
    """Record a 15-second video segment using the camera RIGHT NOW.

    This uses the Raspberry Pi Camera Module 3 to record a 15-second video segment.
    It does NOT retrieve previous metadata from the database

    Returns:
            The newly captured video's metadata: 
            SOURCE, TYPE, TIMESTAMP, DURATION_SECONDS, and FILE_NAME
    """

    return cam_record_video()


available_tools = {
    "sensor_status": sensor_status,
    "read_light": read_light,
    "latest_reading": latest_sensor_reading,
    "latest_camera_metadata": latest_camera_metadata,
    "capture_image": capture_image,
    "record_video": record_video
}

tools = list(available_tools.values())

messages = [
    {
        "role": "system",
        "content": """
You are an IoT assistant running on a Raspberry Pi 5.
Use available tools to retrieve sensor readings and operate the connected camera.

Hardware: 
 - BH1745 luminance and color sensor.
 - Raspberry Pi Camera Module 3.

Tool selection:
 - sensor_status: Check if BH1745 sensor is online.
 - read_light: Obtain a NEW, live BH1745 sensor measurement.
 - latest_reading: Retrieve the most recent measurement stored in the database.
 - capture_image: Capture a still image from the camera RIGHT NOW.
 - record_video: Record a 15-second video from the camera RIGHT NOW.

Rules:
 - For current, live, or up-to-date sensor values, call read_light.
 - For the latest stored or previously recorded sensor measurement, call latest_reading.
 - Never treat a stored measurement as a new live measurement.
 - When asked to capture an image or record a video, call the corresponding camera tool.
 - Never claim a tool operation succeeded unless the tool confirms success.
 - Never invent sensor readings or claim an image or video was captured without tool confirmation.
 - Include timestamps when available.
 - If the request is ambiguous, ask a brief clarifying question.
"""
    }
]

# ~ Possible tool queries:
# ~ "Read the light sensor and tell me its values."
# ~ "What is the current status of the light sensor?"
# ~ "What was the last sensor reading?"
# ~ "What is the lastest entry in the camera database?"
# ~ "How has the light level changed since the last measurement?"
# ~ "Record a video."
# ~ "Take a picture."


# Set keywords for deterministic tool-calling
current_words = (
    "current", "currently", "right now", "live", "present", "up-to-date", "up to date"
)

sensor_words = ("sensor", "BH1745", "light", "luminance", "color")
camera_words = ("camera", "camera module",
                "Raspberry Pi Camera Module 3", "Camera Module 3")

comparison_words = (
    "compare", "difference", "change", "versus", "vs", "against"
)

database_words = (
    "latest stored", "stored reading", "database", "previous reading",
    "last reading", "previous measurement", "last measurement"
)


# User input keyword checks
def asks_for_current_sensor(user_input):
    """Check whether the user is explicitly asking for a current sensor reading."""

    has_current = any(word in user_input.lower() for word in current_words)
    has_sensor = any(word in user_input.lower() for word in sensor_words)
    has_camera = any(word in user_input.lower() for word in camera_words)
    has_comparison = any(word in user_input.lower()
                         for word in comparison_words)

    return has_current and has_sensor and not has_camera and not has_comparison


def asks_for_current_camera(user_input):
    """Check whether the user is explicitly asking to use the camera live."""

    has_current = any(word in user_input.lower() for word in current_words)
    has_camera = any(word in user_input.lower() for word in camera_words)
    has_comparison = any(word in user_input.lower()
                         for word in comparison_words)

    return has_current and has_camera and not has_comparison


def asks_for_sensor_database(user_input):
    """Check whether the user is explicitly asking for a sensor database reading."""

    has_database = any(word in user_input.lower() for word in database_words)
    has_sensor = any(word in user_input.lower() for word in sensor_words)
    has_comparison = any(word in user_input.lower()
                         for word in comparison_words)

    return has_database and has_sensor and not has_comparison


def asks_for_camera_database(user_input):
    """Check whether the user is explicitly asking for a camera database reading."""

    has_database = any(word in user_input.lower() for word in database_words)
    has_camera = any(word in user_input.lower() for word in camera_words)
    has_comparison = any(word in user_input.lower()
                         for word in comparison_words)

    return has_database and has_camera and not has_comparison


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
    if asks_for_current_sensor(user_input):

        result = read_light()

        messages.append({
            "role": "tool",
            "tool_name": "read_light",
            "content": str(result)
        })

        response = chat(
            model="LiquidAI/lfm2.5-350m",
            messages=messages
        )

        messages.append(response.message)

        print("\nAgent:", response.message.content)

    # Force tool call "latest_sensor_reading()" when user explicitly asks
    # for database values for deterministic results
    elif asks_for_sensor_database(user_input):

        result = latest_sensor_reading()

        messages.append({
            "role": "tool",
            "tool_name": "latest_sensor_reading",
            "content": str(result)
        })

        response = chat(
            model="LiquidAI/lfm2.5-350m",
            messages=messages
        )

        messages.append(response.message)

        print("\nAgent:", response.message.content)

    # Force tool call "latest_camera_metadata()" when user explicitly asks
    # for database values for deterministic results
    elif asks_for_camera_database(user_input):

        result = latest_camera_metadata()

        messages.append({
            "role": "tool",
            "tool_name": "latest_camera_metadata",
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
