from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="suggit",
    version="1.0.0",
    description="AI-powered git commit message suggester with local fallback",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Charitra",
    author_email="charitraa@github.com",
    url="https://github.com/charitraa/suggit",
    
    py_modules=[
        "aicommit",
        "git_utils",
        "ai_suggest",
        "local_suggest",
        "ui",
        "git_commit",
        "commit"
    ],

    install_requires=[
        "prompt_toolkit>=3.0.0",
        "google-generativeai>=0.8.0",
    ],

    entry_points={
        "console_scripts": [
            "commit=commit:main",
        ],
    },

    python_requires=">=3.8",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)