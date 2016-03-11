from distutils.core import setup

setup(
    name = "Reflect",
    version = "0.0",
    packages = ["reflect"],
    install_requires = ["imageio", "pydotplus", "numpy", "scipy", "cv2", "pygame", "watchdog"]
)
