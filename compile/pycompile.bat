cd ..
cd text-magnet
python3.12 -m nuitka --standalone --onefile --disable-ccache --include-package=PIL --include-package=github --include-package=keyboard --include-package=dotenv --enable-plugin=tk-inter --include-data-dir=data=data --include-data-dir=img=img --output-dir=publish --enable-plugin=anti-bloat main.py