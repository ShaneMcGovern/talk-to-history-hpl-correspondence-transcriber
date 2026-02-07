#!/bin/bash

uv sync

ollama serve &

until curl -s http://localhost:11434 > /dev/null 2>&1; do 
    echo "Waiting on Ollama..."
    sleep 3
done

wait $!