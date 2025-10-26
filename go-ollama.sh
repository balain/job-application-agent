#!/bin/bash

FILE="John D Lewis resume.docx"

if [ ! -f "$1/$FILE" ]; then
	cp "./applications/templates/John D Lewis resume.docx" "$1/"
fi

uv run main.py -j "$1/Job Description.txt" -r "$1/John D Lewis resume.docx" -o "$1/Job Assessment Ollama.txt" -f text -p ollama
