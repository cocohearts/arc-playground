import streamlit as st
import random
import base64
from io import BytesIO
import re 
import random
from arc.utils.dataset import get_riddles
import numpy as np
import json
from anthropic import Anthropic
from vis_util import plot_one_pil

train_riddles = get_riddles(["training"])

with open("riddles_list.json", "r") as f:
    riddles_list = json.load(f)

def get_riddle_by_id(riddle_id):
    for riddle in train_riddles:
        if riddle.riddle_id == riddle_id:
            return riddle

deepseek_api_key = "sk-3aade99bf89441babb22fdb0556241d7"

anthropic_key = "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"

def encode_image_to_base64(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    byte_data = buffer.getvalue()
    base64_encoded = base64.b64encode(byte_data)
    base64_string = base64_encoded.decode('utf-8')    
    return base64_string


# client = OpenAI(api_key='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')
anthropic_key = "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"
anthropic_key = "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"
client = Anthropic(api_key=anthropic_key)

color_mappings = """
# 0 - black
# 1 - blue
# 2 - red
# 3 - green
# 4 - yellow
# 5 - grey
# 6 - magenta
# 7 - orange
# 8 - light blue
# 9 - maroon
""".strip()

def draw_grid(grid: np.ndarray) -> str:
    grid = grid.astype(int)
    return "\n".join([" | ".join([str(x) for x in row]) for row in grid])

def _make_gpt_prompt(riddle, command):
    test_grid = riddle.test[0].input.np
    test_grid_img = encode_image_to_base64(plot_one_pil(test_grid))
    grid_text = draw_grid(test_grid)

    train_examples = [(riddle.train[i].input.np, riddle.train[i].output.np) for i in range(len(riddle.train))]
    train_examples_str = [
        {
            "type": "text",
            "text": f"Example {i + 1}:\n```input_grid\n{draw_grid(input)}\n```\n\n Output:\n```output_grid\n{draw_grid(output)}\n```\n",
        }
        for i, (input, output) in enumerate(train_examples)
    ]

    user_content = [
        {
            "type": "text",
            "text": "I am trying to solve the ARC Prize. Here is an input grid represented as an image.",
        },
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data":test_grid_img},
        },
        {
            "type": "text",
            "text": "Here are some training examples:",
        },
        *train_examples_str,
        {
            "type": "text",
            "text": (
                f"Here is a text representation of the grid:\n```input_grid\n{grid_text}\n```\n\n"
                + f"Here are the color mappings between the image and text representation:\n```{color_mappings}```\n\n"
                + f"Produce a new grid text representation (wrapped with ```answer and ```) according to the following rule: `{command}`\n\n"
            ),
        },
    ]
    return user_content

def interpret_command(riddle, command):
    user_content = _make_gpt_prompt(riddle, command)
    response = client.messages.create(
        # model="claude-3-5-sonnet-20240620",
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": user_content}],
        max_tokens=1024,
    )
    # res = response.choices[0].message.content
    res = response.content[0].text
    try:
        pattern = r"```\s*answer\s*(.*?)\s*```"
        parsed_grid = re.search(pattern, res, re.DOTALL).group(1).strip()
        parsed_grid = [list(map(int, row.split(" | "))) for row in parsed_grid.split("\n")]
        return np.array(parsed_grid), res
    except:
        return None, res

def run_riddle(riddle_id, command):
    riddle = get_riddle_by_id(riddle_id)
    out_grid, raw_res = interpret_command(riddle, command)
    return out_grid, raw_res

# Initialize session state for riddle ID if not already present
if 'riddle_id' not in st.session_state:
    st.session_state.riddle_id = random.choice(riddles_list)

st.title("ARC Interpreter")

# Display the current riddle ID
st.write(f"Selected riddle ID: {st.session_state.riddle_id}")

# Retrieve the riddle based on the stored or newly selected riddle ID
new_riddle = get_riddle_by_id(st.session_state.riddle_id)
train = new_riddle.train

# Display corresponding input and output images next to each other with consistent spacing
st.write("Training Examples:")
for i in range(len(train)):
    cols = st.columns([1, 1, 1, 1])  # Create five columns for better centering
    with cols[1]:  # Input images in the second column
        st.image(plot_one_pil(train[i].input.np), caption="Input", width=150)
    with cols[2]:  # Output images in the third column
        st.image(plot_one_pil(train[i].output.np), caption="Output", width=150)

# Display the test input image centered and of the same small size
st.write("Test Input Image:")
cols = st.columns([1, 1, 1])  # Create three columns for better centering
with cols[1]:  # Center the test input image in the middle column
    st.image(plot_one_pil(new_riddle.test[0].input.np), caption="Test Input", use_column_width=True)

command = st.text_input("Enter a command:")

if st.button("Run"):
    out_grid, raw_res = run_riddle(st.session_state.riddle_id, command)
    cols = st.columns([1, 1, 1])
    with cols[1]:
        st.image(plot_one_pil(out_grid), caption="Test Output", use_column_width=True)
    # st.text(raw_res)


# Add a button to refresh the entire state
if st.button("New Riddle"):
    # Clear all session state
    st.session_state.clear()
    # Rerun the app from the top after clearing state
    st.experimental_rerun()