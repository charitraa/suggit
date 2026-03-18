from setuptools import setup, find_packages

setup(
    name="suggit",
    version="1.0.0",
    description="AI-powered git commit message suggester with local fallback",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Charitra",
    author_email="charitraa@github.com",
    url="https://github.com/charitraa/suggit",
    py_modules=["commit", "git_utils", "ai_suggest", "local_suggest", "ui"],
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
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
