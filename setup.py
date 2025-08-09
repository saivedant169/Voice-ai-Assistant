"""
Setup script for Voice-Activated AI Assistant
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="voice-ai-assistant",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A sophisticated voice-activated AI assistant using Whisper, GPT, and TTS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/voice-ai-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "azure": [
            "azure-cognitiveservices-speech>=1.32.0",
        ],
        "elevenlabs": [
            "elevenlabs>=0.2.0",
        ],
        "web": [
            "streamlit>=1.28.0",
            "plotly>=5.17.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "voice-assistant=examples.cli_assistant:main",
            "voice-assistant-basic=examples.basic_usage:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="voice assistant ai speech recognition text-to-speech whisper gpt conversation",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/voice-ai-assistant/issues",
        "Source": "https://github.com/yourusername/voice-ai-assistant",
        "Documentation": "https://github.com/yourusername/voice-ai-assistant#readme",
    },
)
