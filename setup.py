from setuptools import setup

setup(
    name="zebv",
    version="0.1",
    author="Zebra Infused Hamsters",
    python_requires=">=3.6",
    packages=["zebv"],
    scripts=[],
    entry_points="""
      [console_scripts]
      py-zebra=zebv.app:main
      """,
    install_requires=["requests", "pillow", "click", "click_log"],
    # install_requires=["requests", "pillow", "click", "click_log", "tcod", "numpy"],
    tests_require=["pytest", "tcod"],
    extras_require={"tests": ["pytest", "tcod"]},
)
