# ScreenCoder: Advancing Visual-to-Code Generation for Front-End Automation via Modular Multimodal Agents

<div align="center">

Yilei Jiang<sup>1*</sup>, Yaozhi Zheng<sup>1*</sup>, Yuxuan Wan<sup>2*</sup>,  
Jiaming Han<sup>1</sup>, Qunzhong Wang<sup>1</sup>,  
Michael R. Lyu<sup>2</sup>, Xiangyu Yue<sup>1✉</sup>  
<br>
<sup>1</sup>CUHK MMLab, <sup>2</sup>CUHK ARISE Lab  
<br>
<sup>*</sup>Equal contribution  <sup>✉</sup>Corresponding author

</div>
<div align="center">
  <img src="teaser.jpg" width="100%"/>
  
</div>

### Project Structure
- `main.py`: The main script to generate final HTML code for a single screenshot.
- `UIED/`: Contains the UIED (UI Element Detection) engine for analyzing screenshots and detecting components.
  - `run_single.py`: Python script to run UI component detection on a single image.
- `html_generator.py`: Takes the detected component data and generates a complete HTML layout with generated code for each module.
- `image_replacer.py`: A script to replace placeholder divs in the final HTML with actual cropped images.
- `mapping.py`: Maps the detected UIED components to logical page regions.
- `requirements.txt`: Lists all the necessary Python dependencies for the project.
- `doubao_api.txt`: API key file for the Doubao model (should be kept private and is included in `.gitignore`).

### Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/JimmyZhengyz/screencoder.git
    cd screencoder
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up API Key:**
    - Create a file named `doubao_api.txt` in the root directory.
    - Paste your Doubao API key into this file.

### Usage

The typical workflow is a multi-step process as follows:

1.  **Initial Generation with Placeholders:**
    Run the Python script to generate the initial HTML code for a given screenshot.
    - Block Detection:
      ```bash
      python block_parsor.py
      ```
    - Generation with Placeholders (Gray Images Blocks):
      ```bash
      python html_generator.py
      ```

2.  **Final HTML Code:**
    Run the python script to generate final HTML code with copped images from the original screenshot.
    - Placeholder Detection:
      ```bash
      python image_box_detection.py
      ```
    - UI Element Detection:
      ```bash
      python UIED/run_single.py
      ```
    - Mapping Alignment Between Placeholders and UI Elements:
      ```bash
      python mapping.py
      ```
    - Placeholder Replacement:
      ```bash
      python image_replacer.py
      ```

3.  **Simple Run:**
    Run the python script to generate the final HTML code:
    ```bash
    python main.py
    ```

