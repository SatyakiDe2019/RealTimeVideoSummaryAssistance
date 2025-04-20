# Real-time video summary assistance App (RVSAA)

![Logos.jpeg](Logos.jpeg)

## About this package

This implementation guide explains how to create a real-time meeting assistant using two different agent frameworks (LangChain and AutoGen) that coordinate via the Message-Chaining Protocol (MCP). For this project, the team has identified the following LLMs: OpenAI, Sarvam AI. This project is for advanced Python, Autogen, Open AI, Sarvam AI, and Google for data Science Newbies and AI evangelists.


## How to use this package

(The following instructions apply to Posix/bash. Windows users should check [here](https://docs.python.org/3/library/venv.html).)

First, clone this repository and open a terminal inside the root folder.

```bash
git clone <repository-url>
cd <repository-directory>
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Install the above requirements.

Create and activate a new virtual environment (recommended) for consumer applications by running the following:

```bash
python3.13 -m venv env
source env/bin/activate
```

Run the server, which will interact with the FAST API & then run the custom Python-based MCP application.

Built-In LLM Monitoring Application: 

```bash
python generateLLMPerformance.py
```

Please find some of the essential dependent packages -

```
pip install autogen==0.8.7
pip install anthropic==0.42.0
pip install fastapi==0.115.12
pip install google-api-core==2.24.2
pip install google-auth==2.39.0
pip install google-cloud-core==2.4.3
pip install google-cloud-translate==3.20.2
pip install googleapis-common-protos==1.70.0
pip install langchain==0.3.23
pip install langchain-community==0.3.21
pip install langchain-core==0.3.54
pip install langchain-openai==0.3.14
pip install langchain-text-splitters==0.3.8
pip install langsmith==0.3.32
pip install lingua-language-detector==2.1.0
pip install numpy==2.2.4
pip install openai==1.75.0
pip install pyautogen==0.8.7
pip install pydantic==2.11.3
pip install pydantic_core==2.33.1
pip install pydantic-settings==2.9.1
pip install redis==5.2.1
pip install regex==2024.11.6
pip install requests==2.32.3
pip install requests-toolbelt==1.0.0
pip install youtube-transcript-api==1.0.3

```

## Screenshots

![demo.GIF](demo.GIF)

## Troubleshooting

### Common Issues:

1. **API Key Errors**:
   - Double-check that you've enabled the required APIs in your cloud accounts

2. **Language Detection Issues**:
   - The Lingua library requires specific language models
   - Make sure you have sufficient disk space for language detection models

3. **Translation Service Failures**:
   - Check your API usage quotas for both Google Cloud and Sarvam AI
   - Verify your internet connection is stable

4. **YouTube Transcript API Errors**:
   - Some videos may have disabled transcripts
   - Private or age-restricted videos might not be accessible

### Checking API Keys:

You can test your API keys individually:

1. **OpenAI API**:
```python
import openai
openai.api_key = "your_openai_api_key"
response = openai.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello!"}])
print(response)
```

2. **Google Cloud Translation API**:
```python
from google.cloud import translate_v2 as translate
client = translate.Client(api_key="your_google_api_key")
result = client.translate("Hello world", target_language="es")
print(result)
```

3. **Sarvam AI API**:
```python
import requests
headers = {"Content-Type": "application/json", "api-subscription-key": "your_sarvam_api_key"}
payload = {"input": "Hello", "source_language_code": "en-IN", "target_language_code": "hi-IN"}
response = requests.post("https://api.sarvam.ai/translate", headers=headers, json=payload)
print(response.json())
```

## Contact

If you encounter any issues not covered in this guide, please contact the project maintainers.

## Resources

- To view the complete demo with sound, check out our [YouTube Page](https://youtu.be/jMERwsokd6Q).
- To view Python, check out the [Python Page](https://docs.python.org/3/).
- To view Sarvam AI, check out the [Anthropic Page](https://docs.sarvam.ai/api-reference-docs/introduction).
- To view Open AI, check out the [OpenAI Page](https://platform.openai.com/docs/api-reference/introduction).
- To view LangChain, check out the [OpenAI Page](https://python.langchain.com/docs/introduction/).
- To view AutoGen, check out the [OpenAI Page](https://microsoft.github.io/autogen/stable//index.html).
