from setuptools import setup, find_packages

setup(
    name='pi-motor-control-project',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Raspberry Pi project for motor control and obstacle avoidance using ultrasonic sensors.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'RPi.GPIO',
        'flask',           # For web interface
        'picamera',        # For camera support
        'numpy',           # For image processing
        'opencv-python',   # For computer vision
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)