#!/bin/bash
huggingface-cli login --token $HUGGINGFACE_TOKEN
python auto_remove_old_file.py &
streamlit run main.py