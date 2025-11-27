cd ..
cd text-magnet
python3.12 -m nuitka --standalone --onefile --include-package=PIL --include-package=keyboard --include-package=requests --include-package=dotenv --enable-plugin=tk-inter --include-data-dir=data=data --include-data-dir=img=img --output-dir=publish --enable-plugin=anti-bloat main.py