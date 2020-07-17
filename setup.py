from setuptools import setup

setup(
    name="icfpcontest2020",
    version="0.1",
    author="Zebra Infused Hamsters",
    python_requires=">=3.8",
    packages=["app"],
    scripts=[],
    entry_points="""
      [console_scripts]
      py-zebra=app:main
      """,
    install_requires=["click", "click_log", "numpy", "requests", "scipy", "pandas"],
)
