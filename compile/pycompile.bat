cd ..
cd text-magnet
python3.12 -m nuitka --standalone --onefile --include-package=PIL --include-package=keyboard --enable-plugin=tk-inter --include-data-dir=data=data --include-data-dir=img=img --include-data-dir=db=db --output-dir=publish main.py